from __future__ import annotations

import logging
import time

from digest.agents.approval import encode_callback
from digest.agents.reporter import RunReport
from digest.core.models import make_id
from digest.core.post_state import PostRecord, PostState
from digest.core.timing import timed

logger = logging.getLogger(__name__)


class Pipeline:
    """Orchestrator core. All collaborators injected for testability."""

    def __init__(
        self, *, ingestor, processor, clusterer, analyst, writer, translator,
        quality_gate, publisher, seen, post_store, reporter, telegram,
        languages, keywords, discovery_enabled, approval_required, repo_dir,
        date, site_url="", max_articles=0, publish_enabled=True, model_mode="both",
    ) -> None:
        self.ingestor = ingestor
        self.processor = processor
        self.clusterer = clusterer
        self.analyst = analyst
        self.writer = writer
        self.translator = translator
        self.quality_gate = quality_gate
        self.publisher = publisher
        self.seen = seen
        self.post_store = post_store
        self.reporter = reporter
        self.telegram = telegram
        self.languages = languages
        self.keywords = keywords
        self.discovery_enabled = discovery_enabled
        self.approval_required = approval_required
        self.repo_dir = repo_dir
        self.date = date
        self.site_url = site_url
        self.max_articles = max_articles
        self.publish_enabled = publish_enabled
        self.model_mode = model_mode

    def run(self) -> RunReport:
        t_start = time.perf_counter()
        report = RunReport(
            site_url=self.site_url, date=self.date[:10] or self.date,
            mode=self.model_mode, approval=self.approval_required,
        )

        with timed("ingest", report.timings):
            articles = self.ingestor.gather(self.keywords, self.discovery_enabled)
            if self.max_articles and len(articles) > self.max_articles:
                articles = self._interleave_by_source(articles)[: self.max_articles]
        report.articles_in = len(articles)
        logger.info("ingested %d articles", len(articles))
        if not articles:
            report.duration_s = time.perf_counter() - t_start
            self.reporter.daily_summary(report)
            return report

        with timed("process", report.timings):
            processed = self.processor.process_many(articles)
        with timed("cluster", report.timings):
            clusters = self.clusterer.cluster(processed)
        with timed("analyze", report.timings):
            digest = self.analyst.analyze(clusters)
        with timed("write", report.timings):
            en_posts = self.writer.write(digest, date=self.date)

        # group: each kept EN post + its VI translation
        groups: list[dict] = []
        with timed("translate+gate", report.timings):
            for en in en_posts:
                # dedup: never re-offer/re-publish a story already decided
                existing = self.post_store.get(self._key(en))
                if existing is not None and existing.state in ("published", "discarded"):
                    report.errors.append(f"skipped duplicate (already {existing.state}): {en.title}")
                    continue
                verdict = self.quality_gate.check(en)
                if not verdict.passed:
                    report.errors.append(f"quality gate rejected: {en.title} ({verdict.reason})")
                    continue
                posts = [en]
                if "vi" in self.languages:
                    posts.append(self.translator.translate(en))
                groups.append({"en": en, "posts": posts})

        all_posts = [p for g in groups for p in g["posts"]]
        report.posts_written = len(groups)
        report.published_titles = [g["en"].title for g in groups]

        if groups:
            with timed("publish", report.timings):
                if self.approval_required:
                    self._write_and_request(groups)
                else:
                    self._write_and_publish(all_posts, report)

        # idempotency: every ingested article is now "seen"
        self.seen.add_many([a.id for a in articles])
        self.seen.save()

        report.duration_s = time.perf_counter() - t_start
        logger.info("run finished in %.1fs", report.duration_s)
        self.reporter.daily_summary(report)
        return report

    def _write_and_request(self, groups) -> None:
        all_posts = [p for g in groups for p in g["posts"]]
        files = self.publisher.write_posts(all_posts, draft=True)
        # strict zip guards against a partial write_posts result silently dropping posts
        files_by_post = dict(zip(all_posts, files, strict=True))
        for g in groups:
            en = g["en"]
            key = self._key(en)
            g_files = [str(files_by_post[p]) for p in g["posts"]]
            article_ids = [make_id(u) for u in en.sources]
            buttons = [
                ("✅ Publish", encode_callback("pub", key)),
                ("✏️ Hold", encode_callback("hold", key)),
                ("❌ Discard", encode_callback("disc", key)),
            ]
            mid = self.telegram.send_message(
                f"<b>{en.title}</b>\n{en.category} — {en.summary}", buttons=buttons
            )
            self.post_store.upsert(PostRecord(
                key=key, date=en.date, slug=en.slug, title=en.title,
                state=PostState.PENDING.value, files=g_files,
                article_ids=article_ids, message_id=mid,
            ))

    def _write_and_publish(self, all_posts, report) -> None:
        self.publisher.write_posts(all_posts, draft=False)
        if not self.publish_enabled:
            report.errors.append("dry-run (steps.publish=false): files written, not pushed")
            return
        self.publisher.commit_and_push("post: daily digest", repo_dir=self.repo_dir)
        report.published = len({p.slug for p in all_posts})

    @staticmethod
    def _key(post) -> str:
        # day (not full datetime) + capped slug -> callback_data stays <64 bytes,
        # and the same story on the same day dedups even across runs.
        return f"{post.date[:10]}:{post.slug[:47]}"

    @staticmethod
    def _interleave_by_source(articles):
        """Round-robin articles across their sources so a cap keeps diversity
        instead of taking N items from whichever feed came first."""
        from collections import OrderedDict

        buckets: "OrderedDict[str, list]" = OrderedDict()
        for a in articles:
            buckets.setdefault(a.source, []).append(a)
        out: list = []
        queues = list(buckets.values())
        while queues:
            for q in list(queues):
                if q:
                    out.append(q.pop(0))
                if not q:
                    queues.remove(q)
        return out
