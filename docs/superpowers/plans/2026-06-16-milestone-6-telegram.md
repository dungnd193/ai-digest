# Milestone 6: Telegram + Orchestration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: subagent-driven-development / executing-plans. Checkbox steps. Strict TDD. Commit per task with the `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` trailer.

**Goal:** Wire the whole pipeline together behind two entrypoints — `orchestrator.py` (cron: ingest → process → write → publish-or-hold) and `approver.py` (long-polling service: handle Telegram approval buttons) — with a post state machine, a Telegram client, and a Reporter for daily summary + error alerts.

**Architecture:** A thin `TelegramClient` wraps the Bot HTTP API (sendMessage with inline keyboards, getUpdates long-poll, answerCallbackQuery, editMessageText) over `requests` — no heavy library, fully mockable. `PostStore` persists each post's lifecycle (`draft → pending_approval → published | held | discarded`) to `state/posts.json`. `Reporter` formats daily-summary and error (cause + fix) messages. `ApprovalService` applies a button decision (publish/hold/discard) to files + state + seen. `Pipeline` is the orchestrator core with every collaborator injected (testable with mocks); `orchestrator.py`/`approver.py` are thin mains that build real collaborators. The `approval_required` setting selects publish-now vs hold-for-approval.

**Tech Stack:** Python 3.14, `uv`, `pytest`, `requests`. Reuses every prior milestone.

---

## Conventions
- Repo root `~/Desktop/Workspace/ai-digest`, branch `feat/milestones`.
- `export PATH="$HOME/.local/bin:$PATH"` before `uv`. Tests mock all I/O (no real Telegram, git, or models).

## File structure
```
digest/
├── core/
│   ├── post_state.py        # PostState, PostRecord, PostStore
│   └── telegram.py          # TelegramClient
├── agents/
│   ├── reporter.py          # Reporter (daily summary + error alert)
│   └── approval.py          # callback encode/decode + ApprovalService
├── pipeline.py              # Pipeline (orchestrator core)
├── orchestrator.py          # entrypoint: cron run
├── approver.py              # entrypoint: long-polling approval service
└── tests/ test_post_state.py test_telegram.py test_reporter.py
         test_approval.py test_pipeline.py
```
Also MODIFY `digest/agents/publisher.py` to add `mark_published(paths)`.

---

## Task 1: Post state machine + store

**Files:** Create `digest/core/post_state.py`; Test `digest/tests/test_post_state.py`

- [ ] **Step 1: Failing tests**
```python
from digest.core.post_state import PostRecord, PostState, PostStore


def _rec(key="2026-06-16:ai-agents"):
    return PostRecord(
        key=key, date="2026-06-16", slug="ai-agents", title="T",
        state=PostState.PENDING.value, files=["a.en.md"], article_ids=["id1"],
        message_id=None,
    )


def test_store_upsert_and_get(tmp_path):
    store = PostStore(tmp_path / "posts.json")
    store.upsert(_rec())
    got = store.get("2026-06-16:ai-agents")
    assert got.title == "T"
    assert got.state == "pending_approval"


def test_store_persists(tmp_path):
    path = tmp_path / "posts.json"
    PostStore(path).upsert(_rec()); PostStore(path)  # reload
    store2 = PostStore(path)
    store2.upsert(_rec())  # idempotent reload works
    assert store2.get("2026-06-16:ai-agents") is not None


def test_store_set_state_and_pending(tmp_path):
    store = PostStore(tmp_path / "posts.json")
    store.upsert(_rec())
    store.set_state("2026-06-16:ai-agents", PostState.PUBLISHED)
    assert store.get("2026-06-16:ai-agents").state == "published"
    assert store.pending() == []  # no longer pending


def test_store_pending_lists_only_pending(tmp_path):
    store = PostStore(tmp_path / "posts.json")
    store.upsert(_rec("k1"))
    r2 = _rec("k2"); store.upsert(r2)
    store.set_state("k2", PostState.PUBLISHED)
    assert [r.key for r in store.pending()] == ["k1"]
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/core/post_state.py`:
```python
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path


class PostState(str, Enum):
    DRAFT = "draft"
    PENDING = "pending_approval"
    PUBLISHED = "published"
    HELD = "held"
    DISCARDED = "discarded"


@dataclass
class PostRecord:
    key: str
    date: str
    slug: str
    title: str
    state: str
    files: list[str] = field(default_factory=list)
    article_ids: list[str] = field(default_factory=list)
    message_id: int | None = None


class PostStore:
    """Persists post lifecycle records to JSON, keyed by `key` (date:slug)."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._records: dict[str, PostRecord] = {}
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as fh:
                for k, v in json.load(fh).items():
                    self._records[k] = PostRecord(**v)

    def get(self, key: str) -> PostRecord | None:
        return self._records.get(key)

    def upsert(self, record: PostRecord) -> None:
        self._records[record.key] = record
        self.save()

    def set_state(self, key: str, state: PostState) -> None:
        rec = self._records[key]
        rec.state = state.value
        self.save()

    def pending(self) -> list[PostRecord]:
        return [r for r in self._records.values() if r.state == PostState.PENDING.value]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump({k: asdict(v) for k, v in self._records.items()}, fh, indent=2)
```

- [ ] **Step 4: Run → pass** (4 passed). **Step 5: Commit** `feat: post state machine + PostStore`.

---

## Task 2: TelegramClient

**Files:** Create `digest/core/telegram.py`; Test `digest/tests/test_telegram.py`

- [ ] **Step 1: Failing tests**
```python
from unittest.mock import MagicMock, patch

import pytest

from digest.core.telegram import TelegramClient, TelegramError


def _resp(ok=True, result=None):
    m = MagicMock()
    m.raise_for_status.return_value = None
    m.json.return_value = {"ok": ok, "result": result if result is not None else {}}
    return m


def test_send_message_returns_message_id():
    with patch("digest.core.telegram.requests.post",
               return_value=_resp(result={"message_id": 42})) as post:
        mid = TelegramClient("tok", "chat").send_message("hi")
    assert mid == 42
    url = post.call_args.args[0]
    assert url.endswith("/sendMessage")
    assert post.call_args.kwargs["json"]["chat_id"] == "chat"
    assert post.call_args.kwargs["json"]["text"] == "hi"


def test_send_message_with_buttons_builds_inline_keyboard():
    with patch("digest.core.telegram.requests.post",
               return_value=_resp(result={"message_id": 1})) as post:
        TelegramClient("tok", "chat").send_message(
            "pick", buttons=[("Yes", "pub:k"), ("No", "disc:k")]
        )
    markup = post.call_args.kwargs["json"]["reply_markup"]
    row = markup["inline_keyboard"][0]
    assert row[0] == {"text": "Yes", "callback_data": "pub:k"}
    assert row[1] == {"text": "No", "callback_data": "disc:k"}


def test_get_updates_returns_results():
    upd = [{"update_id": 5, "callback_query": {"id": "q", "data": "pub:k"}}]
    with patch("digest.core.telegram.requests.post", return_value=_resp(result=upd)):
        out = TelegramClient("tok", "chat").get_updates(offset=4)
    assert out == upd


def test_raises_telegramerror_on_http_failure():
    with patch("digest.core.telegram.requests.post", side_effect=Exception("boom")):
        with pytest.raises(TelegramError):
            TelegramClient("tok", "chat").send_message("hi")
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/core/telegram.py`:
```python
from __future__ import annotations

import requests


class TelegramError(RuntimeError):
    """Raised when a Telegram Bot API call fails."""


class TelegramClient:
    """Thin wrapper over the Telegram Bot HTTP API (no external bot library)."""

    def __init__(self, token: str, chat_id: str, timeout: int = 30) -> None:
        self.base = f"https://api.telegram.org/bot{token}"
        self.chat_id = chat_id
        self.timeout = timeout

    def _call(self, method: str, payload: dict) -> dict:
        try:
            resp = requests.post(f"{self.base}/{method}", json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            raise TelegramError(f"{method} failed: {exc}") from exc
        if not data.get("ok", False):
            raise TelegramError(f"{method} returned not ok: {data}")
        return data.get("result", {})

    def send_message(self, text: str, *, buttons: list[tuple[str, str]] | None = None) -> int:
        payload: dict = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
        if buttons:
            payload["reply_markup"] = {
                "inline_keyboard": [
                    [{"text": label, "callback_data": data} for label, data in buttons]
                ]
            }
        return self._call("sendMessage", payload)["message_id"]

    def edit_message_text(self, message_id: int, text: str) -> None:
        self._call("editMessageText", {
            "chat_id": self.chat_id, "message_id": message_id,
            "text": text, "parse_mode": "HTML",
        })

    def answer_callback(self, callback_query_id: str, text: str = "") -> None:
        self._call("answerCallbackQuery", {"callback_query_id": callback_query_id, "text": text})

    def get_updates(self, offset: int | None = None, timeout: int = 25) -> list[dict]:
        payload: dict = {"timeout": timeout, "allowed_updates": ["callback_query"]}
        if offset is not None:
            payload["offset"] = offset
        return self._call("getUpdates", payload)
```

- [ ] **Step 4: Run → pass** (4 passed). **Step 5: Commit** `feat: TelegramClient over Bot HTTP API`.

---

## Task 3: Reporter

**Files:** Create `digest/agents/reporter.py`; Test `digest/tests/test_reporter.py`

- [ ] **Step 1: Failing tests**
```python
from unittest.mock import MagicMock

from digest.agents.reporter import Reporter, RunReport


def test_daily_summary_sends_counts():
    tg = MagicMock(); tg.send_message.return_value = 7
    report = RunReport(articles_in=12, posts_written=3, published=3, errors=[], site_url="https://x")
    mid = Reporter(tg).daily_summary(report)
    assert mid == 7
    text = tg.send_message.call_args.args[0]
    assert "12" in text and "3" in text and "https://x" in text


def test_daily_summary_includes_error_count():
    tg = MagicMock()
    report = RunReport(articles_in=5, posts_written=1, published=0, errors=["feed X failed"])
    Reporter(tg).daily_summary(report)
    text = tg.send_message.call_args.args[0]
    assert "feed X failed" in text


def test_error_alert_has_cause_and_fix():
    tg = MagicMock()
    Reporter(tg).error_alert(stage="Writer", cause="claude timeout", fix="check quota")
    text = tg.send_message.call_args.args[0]
    assert "Writer" in text and "claude timeout" in text and "check quota" in text
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/agents/reporter.py`:
```python
from __future__ import annotations

from dataclasses import dataclass, field

from digest.core.telegram import TelegramClient


@dataclass
class RunReport:
    articles_in: int = 0
    posts_written: int = 0
    published: int = 0
    errors: list[str] = field(default_factory=list)
    site_url: str = ""


class Reporter:
    """Sends a daily summary and error alerts (cause + fix) to Telegram."""

    def __init__(self, telegram: TelegramClient) -> None:
        self.telegram = telegram

    def daily_summary(self, report: RunReport) -> int:
        lines = [
            "<b>AI Digest — daily run</b>",
            f"Articles ingested: {report.articles_in}",
            f"Posts written: {report.posts_written}",
            f"Published: {report.published}",
        ]
        if report.errors:
            lines.append(f"Errors ({len(report.errors)}):")
            lines.extend(f"• {e}" for e in report.errors)
        if report.site_url:
            lines.append(f"Site: {report.site_url}")
        return self.telegram.send_message("\n".join(lines))

    def error_alert(self, *, stage: str, cause: str, fix: str) -> int:
        text = (
            f"❌ <b>{stage} failed</b>\n"
            f"Cause: {cause}\n"
            f"Fix: {fix}"
        )
        return self.telegram.send_message(text)
```

- [ ] **Step 4: Run → pass** (3 passed). **Step 5: Commit** `feat: Reporter (daily summary + error alert)`.

---

## Task 4: Publisher.mark_published (modify)

**Files:** Modify `digest/agents/publisher.py`; Test append to `digest/tests/test_publisher.py`

- [ ] **Step 1: Failing test** — append:
```python
def test_mark_published_flips_draft_flag(tmp_path):
    from digest.agents.publisher import Publisher
    f = tmp_path / "p.md"
    f.write_text("---\ndraft: true\n---\n\nBody.\n", encoding="utf-8")
    Publisher(site_dir=tmp_path).mark_published([f])
    assert "draft: false" in f.read_text(encoding="utf-8")
    assert "draft: true" not in f.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** — add to `Publisher`:
```python
    def mark_published(self, paths: list) -> None:
        """Flip draft front-matter to published for already-written files."""
        from pathlib import Path as _Path
        for p in paths:
            path = _Path(p)
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace("draft: true", "draft: false", 1), encoding="utf-8")
```

- [ ] **Step 4: Run → pass.** **Step 5: Commit** `feat: Publisher.mark_published flips draft flag`.

---

## Task 5: Approval (callback codec + ApprovalService)

**Files:** Create `digest/agents/approval.py`; Test `digest/tests/test_approval.py`

Behavior: callback data is `"<action>:<key>"` where action ∈ {pub, hold, disc}. `ApprovalService.apply(action, key)` mutates files + state + seen:
- `pub`: `publisher.mark_published(files)`, `publisher.commit_and_push(...)`, mark `article_ids` seen + save, state→PUBLISHED. Returns a confirmation string.
- `hold`: state→HELD.
- `disc`: delete files, mark `article_ids` seen + save (so not regenerated), state→DISCARDED.

- [ ] **Step 1: Failing tests**
```python
from unittest.mock import MagicMock

import pytest

from digest.agents.approval import ApprovalService, decode_callback, encode_callback
from digest.core.post_state import PostRecord, PostState, PostStore


def test_codec_roundtrip():
    assert decode_callback(encode_callback("pub", "2026-06-16:slug")) == ("pub", "2026-06-16:slug")


def test_decode_rejects_bad_action():
    with pytest.raises(ValueError):
        decode_callback("nope:key")


def _service(tmp_path):
    store = PostStore(tmp_path / "posts.json")
    f = tmp_path / "a.en.md"; f.write_text("---\ndraft: true\n---\n\nx\n")
    store.upsert(PostRecord(
        key="k", date="2026-06-16", slug="s", title="T", state=PostState.PENDING.value,
        files=[str(f)], article_ids=["id1"], message_id=1,
    ))
    publisher = MagicMock()
    seen = MagicMock()
    svc = ApprovalService(store=store, publisher=publisher, seen=seen, repo_dir=str(tmp_path))
    return svc, store, publisher, seen, f


def test_apply_publish(tmp_path):
    svc, store, publisher, seen, f = _service(tmp_path)
    svc.apply("pub", "k")
    publisher.mark_published.assert_called_once()
    publisher.commit_and_push.assert_called_once()
    seen.add_many.assert_called_once_with(["id1"])
    seen.save.assert_called_once()
    assert store.get("k").state == "published"


def test_apply_hold(tmp_path):
    svc, store, publisher, seen, f = _service(tmp_path)
    svc.apply("hold", "k")
    assert store.get("k").state == "held"
    publisher.commit_and_push.assert_not_called()


def test_apply_discard_deletes_files_and_marks_seen(tmp_path):
    svc, store, publisher, seen, f = _service(tmp_path)
    svc.apply("disc", "k")
    assert not f.exists()
    seen.add_many.assert_called_once_with(["id1"])
    assert store.get("k").state == "discarded"
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/agents/approval.py`:
```python
from __future__ import annotations

import logging
from pathlib import Path

from digest.agents.publisher import Publisher
from digest.core.post_state import PostState, PostStore
from digest.core.state import SeenStore

logger = logging.getLogger(__name__)

_ACTIONS = {"pub", "hold", "disc"}


def encode_callback(action: str, key: str) -> str:
    if action not in _ACTIONS:
        raise ValueError(f"bad action: {action}")
    return f"{action}:{key}"


def decode_callback(data: str) -> tuple[str, str]:
    action, _, key = data.partition(":")
    if action not in _ACTIONS or not key:
        raise ValueError(f"bad callback data: {data!r}")
    return action, key


class ApprovalService:
    """Applies an approval decision to files, post state, and the seen store."""

    def __init__(
        self,
        *,
        store: PostStore,
        publisher: Publisher,
        seen: SeenStore,
        repo_dir: str,
    ) -> None:
        self.store = store
        self.publisher = publisher
        self.seen = seen
        self.repo_dir = repo_dir

    def apply(self, action: str, key: str) -> str:
        rec = self.store.get(key)
        if rec is None:
            return f"Unknown post: {key}"

        if action == "pub":
            self.publisher.mark_published(rec.files)
            self.publisher.commit_and_push(f"post: {rec.title}", repo_dir=self.repo_dir)
            self._mark_seen(rec.article_ids)
            self.store.set_state(key, PostState.PUBLISHED)
            return f"✅ Published: {rec.title}"

        if action == "hold":
            self.store.set_state(key, PostState.HELD)
            return f"✏️ Held: {rec.title}"

        if action == "disc":
            for f in rec.files:
                try:
                    Path(f).unlink(missing_ok=True)
                except OSError as exc:
                    logger.warning("could not delete %s: %s", f, exc)
            self._mark_seen(rec.article_ids)
            self.store.set_state(key, PostState.DISCARDED)
            return f"❌ Discarded: {rec.title}"

        return f"Unknown action: {action}"

    def _mark_seen(self, ids: list[str]) -> None:
        self.seen.add_many(ids)
        self.seen.save()
```

- [ ] **Step 4: Run → pass** (5 passed). **Step 5: Commit** `feat: approval codec + ApprovalService`.

---

## Task 6: Pipeline (orchestrator core)

**Files:** Create `digest/pipeline.py`; Test `digest/tests/test_pipeline.py`

Behavior of `Pipeline.run()`:
1. `articles = ingestor.gather(keywords, discovery_enabled)`
2. `processed = processor.process_many(articles)`
3. `clusters = clusterer.cluster(processed)`
4. `digest = analyst.analyze(clusters)`
5. `en_posts = writer.write(digest, date=date)`
6. For each EN post: if `quality_gate.check(post).passed` → keep it; collect VI translation too if `"vi"` in languages. (Failed gate → add to errors, skip.)
7. If `approval_required`: `publisher.write_posts(all_posts, draft=True)`; for each EN post create a pending `PostRecord` and send a Telegram message with buttons (pub/hold/disc), storing message_id.
   Else: `publisher.write_posts(all_posts, draft=False)`; `publisher.commit_and_push(...)`.
8. Mark ALL ingested article ids seen + save (idempotency) in BOTH modes.
9. `reporter.daily_summary(report)`; return the `RunReport`.

- [ ] **Step 1: Failing tests** `digest/tests/test_pipeline.py`:
```python
from unittest.mock import MagicMock

from digest.core.content_types import BlogPost, QualityVerdict
from digest.core.digest_types import Digest, DigestEntry
from digest.core.models import Article
from digest.pipeline import Pipeline


def _en_post(slug="s"):
    return BlogPost(lang="en", title="T", slug=slug, date="2026-06-16",
                    category="Tools", tags=("ai",), summary="sum", body="b",
                    sources=("https://a.com",))


def _build(**over):
    art = Article.create(url="https://a.com", title="A", source="F")
    deps = dict(
        ingestor=MagicMock(), processor=MagicMock(), clusterer=MagicMock(),
        analyst=MagicMock(), writer=MagicMock(), translator=MagicMock(),
        quality_gate=MagicMock(), publisher=MagicMock(), seen=MagicMock(),
        post_store=MagicMock(), reporter=MagicMock(), telegram=MagicMock(),
        languages=["en", "vi"], keywords=["k"], discovery_enabled=True,
        approval_required=True, repo_dir="/tmp/repo", date="2026-06-16",
        site_url="https://x",
    )
    deps.update(over)
    deps["ingestor"].gather.return_value = [art]
    deps["processor"].process_many.return_value = ["p"]
    deps["clusterer"].cluster.return_value = ["c"]
    deps["analyst"].analyze.return_value = Digest(entries=(DigestEntry(
        title="T", category="Tools", summary="sum", importance=4,
        sources=("https://a.com",), tags=("ai",)),))
    deps["writer"].write.return_value = [_en_post()]
    deps["translator"].translate.return_value = _en_post(slug="s")  # vi stand-in
    deps["quality_gate"].check.return_value = QualityVerdict(passed=True, reason="ok")
    deps["telegram"].send_message.return_value = 99
    return deps


def test_pipeline_approval_mode_writes_drafts_and_sends_buttons():
    deps = _build(approval_required=True)
    report = Pipeline(**deps).run()
    # drafts written
    assert deps["publisher"].write_posts.call_args.kwargs["draft"] is True
    # no auto commit in approval mode
    deps["publisher"].commit_and_push.assert_not_called()
    # telegram buttons sent, pending record stored
    assert deps["telegram"].send_message.called
    assert deps["post_store"].upsert.called
    # seen marked + saved
    deps["seen"].add_many.assert_called_once()
    deps["seen"].save.assert_called_once()
    assert report.posts_written >= 1


def test_pipeline_autopublish_mode_commits_and_pushes():
    deps = _build(approval_required=False)
    report = Pipeline(**deps).run()
    assert deps["publisher"].write_posts.call_args.kwargs["draft"] is False
    deps["publisher"].commit_and_push.assert_called_once()
    deps["telegram"].send_message.assert_called()  # daily summary still sent
    assert report.published >= 1


def test_pipeline_translates_when_vi_enabled():
    deps = _build(languages=["en", "vi"])
    Pipeline(**deps).run()
    deps["translator"].translate.assert_called()


def test_pipeline_skips_translation_when_only_en():
    deps = _build(languages=["en"])
    Pipeline(**deps).run()
    deps["translator"].translate.assert_not_called()


def test_pipeline_failed_quality_gate_skips_post():
    deps = _build(approval_required=False)
    deps["quality_gate"].check.return_value = QualityVerdict(passed=False, reason="bad")
    report = Pipeline(**deps).run()
    # nothing published, but seen still marked (articles were processed)
    assert report.published == 0
    deps["seen"].add_many.assert_called_once()
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/pipeline.py`:
```python
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
        # map files back per group by slug+lang filename order is parallel to all_posts
        from digest.core.render import post_filename
        path_by_name = {self.publisher.posts_dir.name: None}  # placeholder; resolve below
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
```
NOTE for implementer: the `post_filename`/`path_by_name` placeholder line above is dead — remove it. The working mapping is `files_by_post = dict(zip(all_posts, files))`. Keep only that.

- [ ] **Step 4: Run → pass** (5 passed). **Step 5: Commit** `feat: Pipeline orchestrator core (approval + autopublish)`.

---

## Task 7: Entrypoints `orchestrator.py` and `approver.py`

**Files:** Create `digest/orchestrator.py`, `digest/approver.py`; Test `digest/tests/test_entrypoints.py`

These are thin: build real collaborators from config/env, then delegate. Keep logic in builder functions so they're import-safe and lightly testable (no network at import).

- [ ] **Step 1: Failing test** `digest/tests/test_entrypoints.py`:
```python
import importlib


def test_entrypoints_import_without_side_effects():
    # importing must not call network/models
    importlib.import_module("digest.orchestrator")
    importlib.import_module("digest.approver")


def test_orchestrator_has_main():
    mod = importlib.import_module("digest.orchestrator")
    assert hasattr(mod, "main")


def test_approver_has_main_and_handle_update():
    mod = importlib.import_module("digest.approver")
    assert hasattr(mod, "main")
    assert hasattr(mod, "handle_update")
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/orchestrator.py`:
```python
from __future__ import annotations

import logging
import os
from datetime import date as _date
from pathlib import Path

from digest.agents.analyst import Analyst
from digest.agents.clusterer import Clusterer
from digest.agents.collector import Collector
from digest.agents.discovery import Discovery
from digest.agents.ingestor import Ingestor
from digest.agents.processor import Processor
from digest.agents.quality_gate import QualityGate
from digest.agents.reporter import Reporter
from digest.agents.translator import Translator
from digest.agents.writer import Writer
from digest.agents.publisher import Publisher
from digest.core.config import load_env, load_settings
from digest.core.post_state import PostStore
from digest.core.router import build_router
from digest.core.search import build_searcher
from digest.core.state import SeenStore
from digest.core.telegram import TelegramClient
from digest.pipeline import Pipeline

logging.basicConfig(level=logging.INFO)
_ROOT = Path(__file__).resolve().parent.parent


def main(run_date: str | None = None) -> None:
    load_env()
    settings = load_settings(_ROOT / "digest" / "config" / "settings.yaml")
    import yaml
    feeds_cfg = yaml.safe_load((_ROOT / "digest" / "config" / "feeds.yaml").read_text())

    router = build_router()
    searcher = build_searcher()
    seen = SeenStore(_ROOT / "digest" / "state" / "seen.json")
    telegram = TelegramClient(
        os.environ.get("TELEGRAM_BOT_TOKEN", ""), os.environ.get("TELEGRAM_CHAT_ID", "")
    )
    pipeline = Pipeline(
        ingestor=Ingestor(Collector(feeds_cfg.get("feeds", [])),
                          Discovery(searcher, router), seen),
        processor=Processor(router, settings.get("categories", [])),
        clusterer=Clusterer(router),
        analyst=Analyst(router),
        writer=Writer(router),
        translator=Translator(router, settings.get("translator_mode", "draft_then_review")),
        quality_gate=QualityGate(router),
        publisher=Publisher(site_dir=_ROOT / "site"),
        seen=seen,
        post_store=PostStore(_ROOT / "digest" / "state" / "posts.json"),
        reporter=Reporter(telegram),
        telegram=telegram,
        languages=settings.get("languages", ["en"]),
        keywords=settings.get("discovery.keywords", []),
        discovery_enabled=settings.get("discovery.enabled", True),
        approval_required=settings.get("approval_required", True),
        repo_dir=str(_ROOT),
        date=run_date or _date.today().isoformat(),
        site_url=os.environ.get("SITE_URL", ""),
    )
    pipeline.run()


if __name__ == "__main__":
    main()
```

`digest/approver.py`:
```python
from __future__ import annotations

import logging
import os
import time
from pathlib import Path

from digest.agents.approval import ApprovalService, decode_callback
from digest.agents.publisher import Publisher
from digest.core.config import load_env
from digest.core.post_state import PostStore
from digest.core.state import SeenStore
from digest.core.telegram import TelegramClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
_ROOT = Path(__file__).resolve().parent.parent


def handle_update(update: dict, service: ApprovalService, telegram: TelegramClient) -> None:
    """Process one Telegram callback_query update."""
    cq = update.get("callback_query")
    if not cq:
        return
    try:
        action, key = decode_callback(cq.get("data", ""))
    except ValueError:
        telegram.answer_callback(cq["id"], "Unknown action")
        return
    message = service.apply(action, key)
    telegram.answer_callback(cq["id"], message)
    if cq.get("message"):
        telegram.edit_message_text(cq["message"]["message_id"], message)


def build_service() -> tuple[ApprovalService, TelegramClient]:
    load_env()
    telegram = TelegramClient(
        os.environ.get("TELEGRAM_BOT_TOKEN", ""), os.environ.get("TELEGRAM_CHAT_ID", "")
    )
    service = ApprovalService(
        store=PostStore(_ROOT / "digest" / "state" / "posts.json"),
        publisher=Publisher(site_dir=_ROOT / "site"),
        seen=SeenStore(_ROOT / "digest" / "state" / "seen.json"),
        repo_dir=str(_ROOT),
    )
    return service, telegram


def main() -> None:
    service, telegram = build_service()
    offset: int | None = None
    logger.info("approver started; long-polling for approvals")
    while True:
        try:
            updates = telegram.get_updates(offset=offset)
        except Exception as exc:  # noqa: BLE001
            logger.warning("getUpdates failed: %s", exc)
            time.sleep(5)
            continue
        for upd in updates:
            offset = upd["update_id"] + 1
            handle_update(upd, service, telegram)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run → pass** (3 passed). **Step 5: Commit** `feat: orchestrator.py + approver.py entrypoints`.

---

## Task 8: systemd unit + cron docs

**Files:** Create `deploy/ai-digest-approver.service`, `deploy/README.md`

- [ ] **Step 1: `deploy/ai-digest-approver.service`**
```ini
[Unit]
Description=AI Digest Telegram approver (long-polling)
After=network-online.target

[Service]
Type=simple
WorkingDirectory=%h/Desktop/Workspace/ai-digest
Environment=PATH=%h/.local/bin:/usr/bin:/bin
ExecStart=%h/.local/bin/uv run python -m digest.approver
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

- [ ] **Step 2: `deploy/README.md`** — document install:
```markdown
# Deploy

## Approver service (user systemd)
    mkdir -p ~/.config/systemd/user
    cp deploy/ai-digest-approver.service ~/.config/systemd/user/
    systemctl --user daemon-reload
    systemctl --user enable --now ai-digest-approver
    journalctl --user -u ai-digest-approver -f   # logs

## Daily orchestrator (cron)
    crontab -e
    # 7am daily:
    0 7 * * * cd ~/Desktop/Workspace/ai-digest && ~/.local/bin/uv run python -m digest.orchestrator >> digest/state/cron.log 2>&1
```

- [ ] **Step 3: Commit** `docs: systemd approver unit + cron setup`.

---

## Task 9: Full suite check
- [ ] Run `uv run pytest -v`. Expect green (cumulative). Report the number.

## Done criteria for Milestone 6
- PostStore, TelegramClient, Reporter, ApprovalService, Pipeline, and both entrypoints implemented + tested with mocks.
- Approval mode writes drafts + sends inline buttons; autopublish mode commits/pushes; both mark seen.
- `approver.py` handles callbacks and applies decisions; systemd unit + cron documented.
- `uv run pytest` green; all committed.

**Next:** Milestone 7 (Architecture/Docs page) — the LAST task, generating architecture diagrams via the skill.
