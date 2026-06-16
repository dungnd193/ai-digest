from __future__ import annotations

import logging

from digest.agents.approval import encode_callback
from digest.agents.reporter import RunReport
from digest.core.models import make_id
from digest.core.post_state import PostRecord, PostState

logger = logging.getLogger(__name__)


class Pipeline:
    """Orchestrator core. All collaborators injected for testability."""

    def __init__(
        self, *, ingestor, processor, clusterer, analyst, writer, translator,
        quality_gate, publisher, seen, post_store, reporter, telegram,
        languages, keywords, discovery_enabled, approval_required, repo_dir,
        date, site_url="",
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

    def run(self) -> RunReport:
        report = RunReport(site_url=self.site_url)
        articles = self.ingestor.gather(self.keywords, self.discovery_enabled)
        report.articles_in = len(articles)
        if not articles:
            self.reporter.daily_summary(report)
            return report

        processed = self.processor.process_many(articles)
        clusters = self.clusterer.cluster(processed)
        digest = self.analyst.analyze(clusters)
        en_posts = self.writer.write(digest, date=self.date)

        # group: each kept EN post + its VI translation, tracked by slug
        groups: list[dict] = []
        for en in en_posts:
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

        if self.approval_required:
            self._write_and_request(groups, articles)
        else:
            self._write_and_publish(all_posts, report)

        # idempotency: every ingested article is now "seen"
        self.seen.add_many([a.id for a in articles])
        self.seen.save()

        self.reporter.daily_summary(report)
        return report

    def _write_and_request(self, groups, articles) -> None:
        all_posts = [p for g in groups for p in g["posts"]]
        files = self.publisher.write_posts(all_posts, draft=True)
        files_by_post = dict(zip(all_posts, files))
        for g in groups:
            en = g["en"]
            key = f"{en.date}:{en.slug}"
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
        self.publisher.commit_and_push("post: daily digest", repo_dir=self.repo_dir)
        report.published = len({p.slug for p in all_posts})
