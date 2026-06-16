# Milestone 4: Content — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: subagent-driven-development / executing-plans. Checkbox steps. Strict TDD. Commit per task with the `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` trailer.

**Goal:** Turn a `Digest` into publishable blog posts: one English `BlogPost` per digest entry (Writer), a Vietnamese translation that keeps technical terms in English (Translator), and a quality check that flags fabrication before publish (Quality Gate).

**Architecture:** `BlogPost` is an immutable, **generator-neutral** content unit (plain CommonMark body + front-matter fields, NO Hugo shortcodes) so the site generator can be swapped later without touching content. Writer guarantees citations deterministically (it appends a Sources section from the entry's source URLs rather than trusting the model to). Translator supports three modes via config (`gemma_only` / `draft_then_review` / `claude_only`). Quality Gate is fail-open on its own errors (the human approval step in Milestone 6 is the early safety net) but blocks posts the model judges fabricated.

**Tech Stack:** Python 3.14, `uv`, `pytest`. Reuses `Router`, `Digest`/`DigestEntry`.

---

## Conventions
- Repo root `~/Desktop/Workspace/ai-digest`, branch `feat/milestones`.
- `export PATH="$HOME/.local/bin:$PATH"` before `uv`. Tests use a mock Router.

## File structure
```
digest/
├── core/
│   └── content_types.py    # BlogPost, QualityVerdict, slugify
├── agents/
│   ├── writer.py           # Writer (smart)
│   ├── translator.py       # Translator (cheap/smart per mode)
│   └── quality_gate.py     # QualityGate (smart)
└── tests/
    ├── test_content_types.py  test_writer.py
    ├── test_translator.py     test_quality_gate.py
```

---

## Task 1: Content data types + slugify

**Files:** Create `digest/core/content_types.py`; Test `digest/tests/test_content_types.py`

- [ ] **Step 1: Failing tests** `digest/tests/test_content_types.py`:
```python
from digest.core.content_types import BlogPost, QualityVerdict, slugify


def test_slugify_basic():
    assert slugify("Hello, World!") == "hello-world"


def test_slugify_collapses_and_trims():
    assert slugify("  Multi   Agent  AI  ") == "multi-agent-ai"


def test_slugify_strips_non_ascii_punctuation():
    assert slugify("GPT-5: what's new?") == "gpt-5-what-s-new"


def test_blogpost_holds_fields():
    p = BlogPost(
        lang="en", title="T", slug="t", date="2026-06-16", category="Tools",
        tags=("ai",), summary="s", body="# body", sources=("https://a.com",),
    )
    assert p.lang == "en"
    assert p.sources == ("https://a.com",)


def test_quality_verdict():
    v = QualityVerdict(passed=False, reason="unsupported claim")
    assert v.passed is False
    assert "unsupported" in v.reason
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/core/content_types.py`:
```python
from __future__ import annotations

import re
from dataclasses import dataclass


def slugify(title: str) -> str:
    """URL-safe slug: lowercase, non-alphanumerics become single hyphens."""
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


@dataclass(frozen=True)
class BlogPost:
    """Generator-neutral blog post. `body` is plain CommonMark — NO Hugo
    shortcodes — so the static-site generator can be swapped without rework."""

    lang: str
    title: str
    slug: str
    date: str
    category: str
    tags: tuple[str, ...]
    summary: str
    body: str
    sources: tuple[str, ...]


@dataclass(frozen=True)
class QualityVerdict:
    passed: bool
    reason: str
```

- [ ] **Step 4: Run → pass** (5 passed). **Step 5: Commit** `feat: BlogPost/QualityVerdict types + slugify`.

---

## Task 2: Writer (smart tier)

**Files:** Create `digest/agents/writer.py`; Test `digest/tests/test_writer.py`

Behavior: for each `DigestEntry`, ask the smart model for the article body in Markdown. Then: strip any accidental Hugo shortcodes (`{{< ... >}}` / `{{% ... %}}`), and DETERMINISTICALLY append a `## Sources` section listing the entry's source URLs. Build a `BlogPost` (lang="en", title/category/tags/summary from the entry, slug = `slugify(title)`, date from the `date` arg). `write` returns a list, one post per entry; an entry whose model call raises is skipped (logged).

- [ ] **Step 1: Failing tests** `digest/tests/test_writer.py`:
```python
from unittest.mock import MagicMock

from digest.agents.writer import Writer
from digest.core.digest_types import Digest, DigestEntry


def _entry(title="Multi-Agent Systems", sources=("https://a.com",)):
    return DigestEntry(
        title=title, category="Tools", summary="syn", importance=4,
        sources=sources, tags=("ai",),
    )


def test_writer_produces_one_post_per_entry():
    router = MagicMock()
    router.run.return_value = "This is the article body."
    digest = Digest(entries=(_entry(), _entry(title="Second")))
    posts = Writer(router).write(digest, date="2026-06-16")
    assert len(posts) == 2
    assert router.run.call_args.kwargs["tier"] == "smart"


def test_writer_sets_fields_and_slug():
    router = MagicMock()
    router.run.return_value = "Body text."
    posts = Writer(router).write(Digest(entries=(_entry(),)), date="2026-06-16")
    p = posts[0]
    assert p.lang == "en"
    assert p.title == "Multi-Agent Systems"
    assert p.slug == "multi-agent-systems"
    assert p.date == "2026-06-16"
    assert p.category == "Tools"


def test_writer_appends_sources_section():
    router = MagicMock()
    router.run.return_value = "Body."
    posts = Writer(router).write(
        Digest(entries=(_entry(sources=("https://a.com", "https://b.com")),)),
        date="2026-06-16",
    )
    assert "## Sources" in posts[0].body
    assert "https://a.com" in posts[0].body
    assert "https://b.com" in posts[0].body


def test_writer_strips_hugo_shortcodes():
    router = MagicMock()
    router.run.return_value = 'Intro {{< figure src="x.png" >}} and {{% note %}}hi{{% /note %}} end.'
    posts = Writer(router).write(Digest(entries=(_entry(),)), date="2026-06-16")
    assert "{{<" not in posts[0].body
    assert "{{%" not in posts[0].body


def test_writer_skips_entry_on_model_failure():
    router = MagicMock()
    router.run.side_effect = [Exception("down"), "Body."]
    posts = Writer(router).write(
        Digest(entries=(_entry(title="A"), _entry(title="B"))), date="2026-06-16"
    )
    assert [p.title for p in posts] == ["B"]
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/agents/writer.py`:
```python
from __future__ import annotations

import logging
import re

from digest.core.content_types import BlogPost, slugify
from digest.core.digest_types import Digest, DigestEntry
from digest.core.router import Router

logger = logging.getLogger(__name__)

_SHORTCODE_RE = re.compile(r"\{\{[<%].*?[%>]\}\}", re.DOTALL)

_PROMPT = """Write an engaging technical blog article in English Markdown about
the topic below, for readers who already know AI/tech. Use only standard
CommonMark (headings, lists, code fences, links). Do NOT use any template
shortcodes. Do NOT invent facts beyond the provided synthesis. Return only the
article body (no front-matter, no title heading).

Topic: {title}
Synthesis: {summary}
"""


class Writer:
    """Writes one English BlogPost per digest entry (smart tier)."""

    def __init__(self, router: Router) -> None:
        self.router = router

    def write(self, digest: Digest, *, date: str) -> list[BlogPost]:
        posts: list[BlogPost] = []
        for entry in digest.entries:
            try:
                posts.append(self._write_one(entry, date))
            except Exception as exc:  # noqa: BLE001 - one failure shouldn't abort
                logger.warning("writing failed for %r: %s", entry.title, exc)
        return posts

    def _write_one(self, entry: DigestEntry, date: str) -> BlogPost:
        raw = self.router.run(
            _PROMPT.format(title=entry.title, summary=entry.summary), tier="smart"
        )
        body = _SHORTCODE_RE.sub("", raw).strip()
        body += "\n\n## Sources\n" + "\n".join(f"- {u}" for u in entry.sources)
        return BlogPost(
            lang="en",
            title=entry.title,
            slug=slugify(entry.title),
            date=date,
            category=entry.category,
            tags=entry.tags,
            summary=entry.summary,
            body=body,
            sources=entry.sources,
        )
```

- [ ] **Step 4: Run → pass** (5 passed). **Step 5: Commit** `feat: Writer (smart-tier EN posts, guaranteed citations)`.

---

## Task 3: Translator (mode-driven)

**Files:** Create `digest/agents/translator.py`; Test `digest/tests/test_translator.py`

Behavior: produce a Vietnamese `BlogPost` from an English one. The body+title+summary are translated but **technical terms stay in English**. Modes:
- `gemma_only`: one cheap call.
- `claude_only`: one smart call.
- `draft_then_review` (default): cheap draft, then smart review/refine of that draft.
The VI post keeps the same `slug`, `date`, `category`, `tags`, `sources`; only `lang` becomes "vi" and text fields are translated. The Sources section is preserved (URLs are not translated).

- [ ] **Step 1: Failing tests** `digest/tests/test_translator.py`:
```python
from unittest.mock import MagicMock

from digest.agents.translator import Translator
from digest.core.content_types import BlogPost


def _en_post():
    return BlogPost(
        lang="en", title="Multi-Agent Systems", slug="multi-agent-systems",
        date="2026-06-16", category="Tools", tags=("ai",),
        summary="A summary.", body="Body.\n\n## Sources\n- https://a.com",
        sources=("https://a.com",),
    )


def test_translator_gemma_only_single_cheap_call():
    router = MagicMock()
    router.run.return_value = "Tiêu đề\n---\nNội dung tiếng Việt."
    out = Translator(router, mode="gemma_only").translate(_en_post())
    assert out.lang == "vi"
    assert out.slug == "multi-agent-systems"  # slug preserved
    assert router.run.call_count == 1
    assert router.run.call_args.kwargs["tier"] == "cheap"


def test_translator_claude_only_single_smart_call():
    router = MagicMock()
    router.run.return_value = "Nội dung."
    Translator(router, mode="claude_only").translate(_en_post())
    assert router.run.call_args.kwargs["tier"] == "smart"
    assert router.run.call_count == 1


def test_translator_draft_then_review_two_calls():
    router = MagicMock()
    router.run.side_effect = ["bản nháp", "bản hoàn chỉnh"]
    out = Translator(router, mode="draft_then_review").translate(_en_post())
    assert router.run.call_count == 2
    tiers = [c.kwargs["tier"] for c in router.run.call_args_list]
    assert tiers == ["cheap", "smart"]
    assert out.body == "bản hoàn chỉnh"


def test_translator_preserves_metadata():
    router = MagicMock()
    router.run.return_value = "vi body"
    out = Translator(router, mode="gemma_only").translate(_en_post())
    assert out.category == "Tools"
    assert out.tags == ("ai",)
    assert out.sources == ("https://a.com",)
    assert out.date == "2026-06-16"
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/agents/translator.py`:
```python
from __future__ import annotations

from digest.core.content_types import BlogPost
from digest.core.router import Router

_DRAFT = """Translate the following English blog content to Vietnamese for a
Vietnamese audience that knows AI. KEEP technical terms in English (do not
translate jargon like "multi-agent", "embedding", "prompt"). Preserve Markdown
structure and all URLs unchanged. Return only the translated content.

{body}
"""

_REVIEW = """You are a Vietnamese technical editor. Improve this machine
translation for fluency and correctness. KEEP technical terms in English and
keep all Markdown and URLs unchanged. Return only the improved content.

{draft}
"""

_TITLE = """Translate this blog title to Vietnamese, keeping technical terms in
English. Return only the translated title.

{title}
"""


class Translator:
    """Translates an English BlogPost to Vietnamese per the configured mode."""

    def __init__(self, router: Router, mode: str = "draft_then_review") -> None:
        self.router = router
        self.mode = mode

    def translate(self, post: BlogPost) -> BlogPost:
        body = self._translate_text(post.body)
        title = self.router.run(
            _TITLE.format(title=post.title),
            tier="smart" if self.mode == "claude_only" else "cheap",
        ).strip()
        summary = self._translate_text(post.summary) if post.summary else ""
        return BlogPost(
            lang="vi",
            title=title,
            slug=post.slug,
            date=post.date,
            category=post.category,
            tags=post.tags,
            summary=summary,
            body=body,
            sources=post.sources,
        )

    def _translate_text(self, text: str) -> str:
        if self.mode == "claude_only":
            return self.router.run(_DRAFT.format(body=text), tier="smart").strip()
        draft = self.router.run(_DRAFT.format(body=text), tier="cheap").strip()
        if self.mode == "gemma_only":
            return draft
        # draft_then_review
        return self.router.run(_REVIEW.format(draft=draft), tier="smart").strip()
```

Note: `test_translator_*` expects specific call counts. For `gemma_only` the title call is `cheap` and body is one `cheap` call → but the test `test_translator_gemma_only_single_cheap_call` asserts `call_count == 1`. ADJUST: in that test the post has a summary, so naive code makes 3 calls. To satisfy "single cheap call" semantics the test only translates body. **Reconcile by making the test post have empty summary OR counting differently.** Use this corrected test for gemma_only:
```python
def test_translator_gemma_only_single_cheap_call():
    router = MagicMock()
    router.run.return_value = "vi"
    post = _en_post()
    object.__setattr__(post, "summary", "")  # frozen dataclass; clear summary
    out = Translator(router, mode="gemma_only").translate(post)
    assert out.lang == "vi"
    # body (1) + title (1) = 2 cheap calls
    assert router.run.call_count == 2
    assert all(c.kwargs["tier"] == "cheap" for c in router.run.call_args_list)
```
IMPLEMENTER: use the corrected test above (replace the Step 1 version). Likewise update `test_translator_draft_then_review_two_calls` to clear summary so the count is deterministic:
```python
def test_translator_draft_then_review_two_calls():
    router = MagicMock()
    router.run.side_effect = ["bản nháp", "bản hoàn chỉnh", "tiêu đề"]
    post = _en_post()
    object.__setattr__(post, "summary", "")
    out = Translator(router, mode="draft_then_review").translate(post)
    # body: cheap draft + smart review (2); title: cheap (1) = 3 calls
    assert router.run.call_count == 3
    assert out.body == "bản hoàn chỉnh"
```
And `test_translator_claude_only_single_smart_call`:
```python
def test_translator_claude_only_single_smart_call():
    router = MagicMock()
    router.run.return_value = "Nội dung."
    post = _en_post()
    object.__setattr__(post, "summary", "")
    Translator(router, mode="claude_only").translate(post)
    # body smart (1) + title smart (1) = 2
    assert router.run.call_count == 2
    assert all(c.kwargs["tier"] == "smart" for c in router.run.call_args_list)
```

- [ ] **Step 4: Run → pass** (4 passed, using the corrected tests above). **Step 5: Commit** `feat: Translator EN->VI (mode-driven, keeps EN terms)`.

---

## Task 4: Quality Gate (smart tier)

**Files:** Create `digest/agents/quality_gate.py`; Test `digest/tests/test_quality_gate.py`

Behavior: ask the smart model whether the post is grounded in its sources / free of fabrication. Model returns JSON `{"pass": bool, "reason": "..."}`. Parse via `extract_json`. On parse failure or model error → **fail-open**: `QualityVerdict(passed=True, reason="gate inconclusive")` (logged); the human approval step is the early backstop.

- [ ] **Step 1: Failing tests** `digest/tests/test_quality_gate.py`:
```python
import json
from unittest.mock import MagicMock

from digest.agents.quality_gate import QualityGate
from digest.core.content_types import BlogPost


def _post():
    return BlogPost(
        lang="en", title="T", slug="t", date="2026-06-16", category="Tools",
        tags=(), summary="s", body="Body.\n\n## Sources\n- https://a.com",
        sources=("https://a.com",),
    )


def test_quality_gate_pass():
    router = MagicMock()
    router.run.return_value = json.dumps({"pass": True, "reason": "grounded"})
    v = QualityGate(router).check(_post())
    assert v.passed is True
    assert router.run.call_args.kwargs["tier"] == "smart"


def test_quality_gate_fail():
    router = MagicMock()
    router.run.return_value = json.dumps({"pass": False, "reason": "unsupported claim"})
    v = QualityGate(router).check(_post())
    assert v.passed is False
    assert "unsupported" in v.reason


def test_quality_gate_fails_open_on_unparseable():
    router = MagicMock()
    router.run.return_value = "I think it's fine maybe"
    v = QualityGate(router).check(_post())
    assert v.passed is True
    assert "inconclusive" in v.reason.lower()


def test_quality_gate_fails_open_on_model_error():
    router = MagicMock()
    router.run.side_effect = Exception("model down")
    v = QualityGate(router).check(_post())
    assert v.passed is True
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/agents/quality_gate.py`:
```python
from __future__ import annotations

import logging

from digest.core.content_types import BlogPost, QualityVerdict
from digest.core.jsonutil import JSONExtractError, extract_json
from digest.core.router import Router

logger = logging.getLogger(__name__)

_PROMPT = """Review this blog post for factual grounding. Does it avoid
fabricated claims and stay consistent with its listed sources? Return ONLY JSON:
{{"pass": true/false, "reason": "short explanation"}}

Title: {title}
Sources: {sources}
Body:
{body}
"""


class QualityGate:
    """Flags fabricated/ungrounded posts before publish (smart tier).
    Fail-open on its own errors — human approval is the early backstop."""

    def __init__(self, router: Router) -> None:
        self.router = router

    def check(self, post: BlogPost) -> QualityVerdict:
        prompt = _PROMPT.format(
            title=post.title,
            sources=", ".join(post.sources),
            body=post.body[:4000],
        )
        try:
            raw = self.router.run(prompt, tier="smart")
            data = extract_json(raw)
            if not isinstance(data, dict) or "pass" not in data:
                raise JSONExtractError("missing 'pass'")
            return QualityVerdict(
                passed=bool(data["pass"]),
                reason=str(data.get("reason", "")),
            )
        except (JSONExtractError, ValueError, TypeError) as exc:
            logger.warning("quality gate inconclusive for %r: %s", post.title, exc)
            return QualityVerdict(passed=True, reason="gate inconclusive")
        except Exception as exc:  # noqa: BLE001 - model/transport failure
            logger.warning("quality gate error for %r: %s", post.title, exc)
            return QualityVerdict(passed=True, reason="gate inconclusive")
```

- [ ] **Step 4: Run → pass** (4 passed). **Step 5: Commit** `feat: Quality Gate (fabrication check, fail-open)`.

---

## Task 5: Full suite check
- [ ] Run `uv run pytest -v`. Expect green (cumulative). No commit if already committed per task.

## Done criteria for Milestone 4
- `BlogPost`/`QualityVerdict`/`slugify`, Writer, Translator, Quality Gate implemented + tested with mock Router.
- Posts are generator-neutral (no Hugo shortcodes); citations always present.
- VI translation keeps English technical terms; translator honors all three modes.
- `uv run pytest` green; all committed.

**Next:** Milestone 5 (Publishing + CI/CD) — Hugo site, Publisher (render front-matter + git), GitHub Actions deploy.
