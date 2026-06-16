# Milestone 3: Processing — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: subagent-driven-development / executing-plans. Checkbox steps. Strict TDD. Commit per task with the `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` trailer.

**Goal:** Turn raw `Article`s into a structured `Digest`: summarize/categorize/tag each article with the cheap model (Processor), group articles about the same story (Clusterer), then synthesize and prioritize with the smart model (Analyst).

**Architecture:** All three agents call models through the `Router` from Milestone 1. Because LLM output is text, a shared `extract_json` helper robustly parses model responses, and every agent degrades gracefully (a parse failure falls back to a sensible default rather than aborting). Data types: `ProcessedArticle` (article + enrichment), `Cluster` (grouped processed articles), `DigestEntry`/`Digest` (the structured output the Writer in Milestone 4 consumes).

**Tech Stack:** Python 3.14, `uv`, `pytest`. Reuses `digest.core.router.Router`, `digest.core.models.Article`.

---

## Conventions
- Repo root `~/Desktop/Workspace/ai-digest`, branch `feat/milestones`.
- `export PATH="$HOME/.local/bin:$PATH"` before `uv`.
- Tests use a MagicMock Router — NO real model calls.

## File structure
```
digest/
├── core/
│   ├── jsonutil.py        # extract_json + JSONExtractError
│   └── digest_types.py    # ProcessedArticle, Cluster, DigestEntry, Digest
├── agents/
│   ├── processor.py       # Processor (cheap)
│   ├── clusterer.py       # Clusterer (cheap)
│   └── analyst.py         # Analyst (smart)
└── tests/
    ├── test_jsonutil.py  test_processor.py  test_clusterer.py  test_analyst.py
```

---

## Task 1: JSON extraction helper

**Files:** Create `digest/core/jsonutil.py`; Test `digest/tests/test_jsonutil.py`

- [ ] **Step 1: Failing tests** `digest/tests/test_jsonutil.py`:
```python
import pytest

from digest.core.jsonutil import JSONExtractError, extract_json


def test_extract_plain_json_object():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_from_code_fence():
    text = "Here you go:\n```json\n{\"a\": 1, \"b\": [2,3]}\n```\nthanks"
    assert extract_json(text) == {"a": 1, "b": [2, 3]}


def test_extract_json_array_with_surrounding_prose():
    text = "Result: [1, 2, 3] done"
    assert extract_json(text) == [1, 2, 3]


def test_extract_raises_when_no_json():
    with pytest.raises(JSONExtractError):
        extract_json("no json here")
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/core/jsonutil.py`:
```python
from __future__ import annotations

import json
from typing import Any


class JSONExtractError(ValueError):
    """Raised when no parseable JSON value can be found in model output."""


def extract_json(text: str) -> Any:
    """Best-effort parse of a JSON value embedded in LLM text.

    Tries the whole string, then strips code fences, then falls back to the
    substring spanning the first opening bracket to the last matching closing
    bracket. Raises JSONExtractError if nothing parses.
    """
    candidates: list[str] = [text.strip()]

    fenced = text.replace("```json", "```")
    if "```" in fenced:
        parts = fenced.split("```")
        candidates.extend(p.strip() for p in parts if p.strip())

    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        end = text.rfind(closer)
        if start != -1 and end != -1 and end > start:
            candidates.append(text[start : end + 1])

    for cand in candidates:
        try:
            return json.loads(cand)
        except (json.JSONDecodeError, ValueError):
            continue
    raise JSONExtractError(f"no JSON found in: {text[:120]!r}")
```

- [ ] **Step 4: Run → pass** (4 passed). **Step 5: Commit** `feat: robust extract_json for LLM output`.

---

## Task 2: Processing data types

**Files:** Create `digest/core/digest_types.py`; Test `digest/tests/test_digest_types.py`

- [ ] **Step 1: Failing tests** `digest/tests/test_digest_types.py`:
```python
from digest.core.digest_types import Cluster, Digest, DigestEntry, ProcessedArticle
from digest.core.models import Article


def _art(url="https://a.com"):
    return Article.create(url=url, title="T", source="S")


def test_processed_article_holds_enrichment():
    p = ProcessedArticle(
        article=_art(), summary="s", category="Tools", tags=("ai",), points=("p1",)
    )
    assert p.article.url == "https://a.com"
    assert p.category == "Tools"
    assert p.tags == ("ai",)


def test_cluster_groups_processed():
    p = ProcessedArticle(article=_art(), summary="s", category="Tools", tags=(), points=())
    c = Cluster(topic="A topic", items=(p,))
    assert c.items[0] is p


def test_digest_holds_entries():
    e = DigestEntry(
        title="T", category="Tools", summary="syn", importance=4,
        sources=("https://a.com",), tags=("ai",),
    )
    d = Digest(entries=(e,))
    assert d.entries[0].importance == 4
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/core/digest_types.py`:
```python
from __future__ import annotations

from dataclasses import dataclass

from digest.core.models import Article


@dataclass(frozen=True)
class ProcessedArticle:
    article: Article
    summary: str
    category: str
    tags: tuple[str, ...]
    points: tuple[str, ...]


@dataclass(frozen=True)
class Cluster:
    topic: str
    items: tuple[ProcessedArticle, ...]


@dataclass(frozen=True)
class DigestEntry:
    title: str
    category: str
    summary: str
    importance: int
    sources: tuple[str, ...]
    tags: tuple[str, ...]


@dataclass(frozen=True)
class Digest:
    entries: tuple[DigestEntry, ...]
```

- [ ] **Step 4: Run → pass** (3 passed). **Step 5: Commit** `feat: processing/digest data types`.

---

## Task 3: Processor (cheap tier)

**Files:** Create `digest/agents/processor.py`; Test `digest/tests/test_processor.py`

Behavior: for each Article, ask the cheap model for JSON `{summary, category, tags, points}`. Category is constrained to the configured list (fallback to `"Industry"` if the model returns something off-list or output is unparseable). `process_many` is tolerant — an article whose call raises is skipped (logged).

- [ ] **Step 1: Failing tests** `digest/tests/test_processor.py`:
```python
import json
from unittest.mock import MagicMock

from digest.agents.processor import Processor
from digest.core.models import Article

CATEGORIES = ["Research", "Tools", "Industry", "Tutorial", "Opinion"]


def _art(url="https://a.com"):
    return Article.create(url=url, title="T", source="S", content="body")


def test_processor_parses_model_json():
    router = MagicMock()
    router.run.return_value = json.dumps(
        {"summary": "s", "category": "Tools", "tags": ["ai", "llm"], "points": ["p1", "p2"]}
    )
    p = Processor(router, categories=CATEGORIES).process(_art())
    assert p.summary == "s"
    assert p.category == "Tools"
    assert p.tags == ("ai", "llm")
    assert p.points == ("p1", "p2")
    assert router.run.call_args.kwargs["tier"] == "cheap"


def test_processor_falls_back_on_offlist_category():
    router = MagicMock()
    router.run.return_value = json.dumps(
        {"summary": "s", "category": "Nonsense", "tags": [], "points": []}
    )
    p = Processor(router, categories=CATEGORIES).process(_art())
    assert p.category == "Industry"


def test_processor_falls_back_on_unparseable_output():
    router = MagicMock()
    router.run.return_value = "sorry, I cannot"
    p = Processor(router, categories=CATEGORIES).process(_art())
    assert p.category == "Industry"
    assert p.summary  # non-empty fallback (uses article content/title)


def test_process_many_skips_failures():
    router = MagicMock()
    router.run.side_effect = [
        json.dumps({"summary": "s", "category": "Tools", "tags": [], "points": []}),
        Exception("model down"),
    ]
    out = Processor(router, categories=CATEGORIES).process_many([_art("https://a.com"), _art("https://b.com")])
    assert len(out) == 1
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/agents/processor.py`:
```python
from __future__ import annotations

import logging

from digest.core.digest_types import ProcessedArticle
from digest.core.jsonutil import JSONExtractError, extract_json
from digest.core.models import Article
from digest.core.router import Router

logger = logging.getLogger(__name__)

_PROMPT = """You are an analyst. Read the article and return ONLY a JSON object:
{{"summary": "2-3 sentence summary", "category": "<one of: {categories}>",
 "tags": ["lowercase", "keywords"], "points": ["key point 1", "key point 2"]}}

Title: {title}
Content: {content}
"""


class Processor:
    """Per-article enrichment via the cheap model tier."""

    def __init__(self, router: Router, categories: list[str]) -> None:
        self.router = router
        self.categories = categories
        self.default_category = "Industry" if "Industry" in categories else categories[0]

    def process(self, article: Article) -> ProcessedArticle:
        prompt = _PROMPT.format(
            categories=", ".join(self.categories),
            title=article.title,
            content=article.content[:2000],
        )
        raw = self.router.run(prompt, tier="cheap")
        try:
            data = extract_json(raw)
            if not isinstance(data, dict):
                raise JSONExtractError("expected object")
        except JSONExtractError:
            return self._fallback(article)

        category = data.get("category", "")
        if category not in self.categories:
            category = self.default_category
        return ProcessedArticle(
            article=article,
            summary=str(data.get("summary") or article.content[:200] or article.title),
            category=category,
            tags=tuple(str(t) for t in data.get("tags", []) if t),
            points=tuple(str(p) for p in data.get("points", []) if p),
        )

    def _fallback(self, article: Article) -> ProcessedArticle:
        return ProcessedArticle(
            article=article,
            summary=article.content[:200] or article.title,
            category=self.default_category,
            tags=(),
            points=(),
        )

    def process_many(self, articles: list[Article]) -> list[ProcessedArticle]:
        out: list[ProcessedArticle] = []
        for art in articles:
            try:
                out.append(self.process(art))
            except Exception as exc:  # noqa: BLE001 - one bad article shouldn't abort
                logger.warning("processing failed for %s: %s", art.url, exc)
        return out
```

- [ ] **Step 4: Run → pass** (4 passed). **Step 5: Commit** `feat: Processor (cheap-tier enrichment, tolerant)`.

---

## Task 4: Clusterer (cheap tier)

**Files:** Create `digest/agents/clusterer.py`; Test `digest/tests/test_clusterer.py`

Behavior: ask the cheap model to group processed articles covering the same story. Model returns JSON array of index groups, e.g. `[[0,2],[1]]`. Build `Cluster`s. Fallbacks: empty input → `[]`; unparseable output or out-of-range indices → each article its own singleton cluster. Cluster `topic` = title of the first article in the group.

- [ ] **Step 1: Failing tests** `digest/tests/test_clusterer.py`:
```python
import json
from unittest.mock import MagicMock

from digest.agents.clusterer import Clusterer
from digest.core.digest_types import ProcessedArticle
from digest.core.models import Article


def _p(title):
    art = Article.create(url=f"https://{title}.com", title=title, source="S")
    return ProcessedArticle(article=art, summary="s", category="Tools", tags=(), points=())


def test_clusterer_groups_by_model_indices():
    items = [_p("a"), _p("b"), _p("c")]
    router = MagicMock()
    router.run.return_value = json.dumps([[0, 2], [1]])
    clusters = Clusterer(router).cluster(items)
    assert len(clusters) == 2
    assert {i.article.title for i in clusters[0].items} == {"a", "c"}
    assert clusters[0].topic == "a"
    assert router.run.call_args.kwargs["tier"] == "cheap"


def test_clusterer_empty_input_returns_empty():
    assert Clusterer(MagicMock()).cluster([]) == []


def test_clusterer_falls_back_to_singletons_on_bad_output():
    items = [_p("a"), _p("b")]
    router = MagicMock()
    router.run.return_value = "not json"
    clusters = Clusterer(router).cluster(items)
    assert len(clusters) == 2
    assert all(len(c.items) == 1 for c in clusters)


def test_clusterer_ignores_out_of_range_indices():
    items = [_p("a"), _p("b")]
    router = MagicMock()
    router.run.return_value = json.dumps([[0, 99], [1]])
    clusters = Clusterer(router).cluster(items)
    # index 99 dropped; group becomes {a}, plus {b}
    titles = [{i.article.title for i in c.items} for c in clusters]
    assert {"a"} in titles and {"b"} in titles
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/agents/clusterer.py`:
```python
from __future__ import annotations

import logging

from digest.core.digest_types import Cluster, ProcessedArticle
from digest.core.jsonutil import JSONExtractError, extract_json
from digest.core.router import Router

logger = logging.getLogger(__name__)

_PROMPT = """Group these news items that cover the SAME story. Return ONLY a JSON
array of index groups, e.g. [[0,2],[1]]. Every index 0..{n} must appear exactly once.

{listing}
"""


class Clusterer:
    """Groups processed articles about the same story (cheap tier)."""

    def __init__(self, router: Router) -> None:
        self.router = router

    def cluster(self, items: list[ProcessedArticle]) -> list[Cluster]:
        if not items:
            return []
        listing = "\n".join(f"{i}: {p.article.title}" for i, p in enumerate(items))
        raw = self.router.run(
            _PROMPT.format(n=len(items) - 1, listing=listing), tier="cheap"
        )
        try:
            groups = extract_json(raw)
            clusters = self._build(groups, items)
            if clusters:
                return clusters
        except (JSONExtractError, ValueError, TypeError) as exc:
            logger.warning("clustering parse failed, using singletons: %s", exc)
        return [Cluster(topic=p.article.title, items=(p,)) for p in items]

    def _build(self, groups, items: list[ProcessedArticle]) -> list[Cluster]:
        clusters: list[Cluster] = []
        for group in groups:
            members = [items[i] for i in group if isinstance(i, int) and 0 <= i < len(items)]
            if members:
                clusters.append(Cluster(topic=members[0].article.title, items=tuple(members)))
        return clusters
```

- [ ] **Step 4: Run → pass** (4 passed). **Step 5: Commit** `feat: Clusterer (group same-story items, tolerant)`.

---

## Task 5: Analyst (smart tier)

**Files:** Create `digest/agents/analyst.py`; Test `digest/tests/test_analyst.py`

Behavior: from clusters, the smart model produces a `Digest` — one `DigestEntry` per notable cluster with a synthesized summary, an importance score (1-5), category, tags, and source URLs. Model returns JSON array of entry objects. Fallback on parse failure: build one entry per cluster directly from the first item's fields (importance defaulted to 3), so the pipeline still yields a digest.

- [ ] **Step 1: Failing tests** `digest/tests/test_analyst.py`:
```python
import json
from unittest.mock import MagicMock

from digest.agents.analyst import Analyst
from digest.core.digest_types import Cluster, ProcessedArticle
from digest.core.models import Article


def _p(title, url, cat="Tools"):
    art = Article.create(url=url, title=title, source="S")
    return ProcessedArticle(article=art, summary="s", category=cat, tags=("ai",), points=("p",))


def _cluster(title, url):
    return Cluster(topic=title, items=(_p(title, url),))


def test_analyst_builds_digest_from_model_json():
    clusters = [_cluster("Story A", "https://a.com")]
    router = MagicMock()
    router.run.return_value = json.dumps([
        {"title": "Story A", "category": "Tools", "summary": "synthesis",
         "importance": 5, "sources": ["https://a.com"], "tags": ["ai"]}
    ])
    digest = Analyst(router).analyze(clusters)
    assert len(digest.entries) == 1
    e = digest.entries[0]
    assert e.title == "Story A"
    assert e.importance == 5
    assert e.sources == ("https://a.com",)
    assert router.run.call_args.kwargs["tier"] == "smart"


def test_analyst_empty_clusters_returns_empty_digest():
    digest = Analyst(MagicMock()).analyze([])
    assert digest.entries == ()


def test_analyst_falls_back_on_unparseable_output():
    clusters = [_cluster("Story A", "https://a.com")]
    router = MagicMock()
    router.run.return_value = "cannot comply"
    digest = Analyst(router).analyze(clusters)
    assert len(digest.entries) == 1
    assert digest.entries[0].title == "Story A"
    assert digest.entries[0].sources == ("https://a.com",)
    assert 1 <= digest.entries[0].importance <= 5
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/agents/analyst.py`:
```python
from __future__ import annotations

import logging

from digest.core.digest_types import Cluster, Digest, DigestEntry
from digest.core.jsonutil import JSONExtractError, extract_json
from digest.core.router import Router

logger = logging.getLogger(__name__)

_PROMPT = """You are the lead analyst. For each story cluster below, write a
synthesized 3-5 sentence summary and rate its importance 1-5. Return ONLY a JSON
array of objects:
[{{"title": "...", "category": "...", "summary": "...", "importance": 1-5,
   "sources": ["url", ...], "tags": ["..."]}}]

Clusters:
{listing}
"""


class Analyst:
    """Synthesizes a prioritized Digest from clusters (smart tier)."""

    def __init__(self, router: Router) -> None:
        self.router = router

    def analyze(self, clusters: list[Cluster]) -> Digest:
        if not clusters:
            return Digest(entries=())
        listing = self._render(clusters)
        raw = self.router.run(_PROMPT.format(listing=listing), tier="smart")
        try:
            data = extract_json(raw)
            entries = tuple(self._entry(obj) for obj in data)
            if entries:
                return Digest(entries=entries)
        except (JSONExtractError, ValueError, TypeError, KeyError) as exc:
            logger.warning("analyst parse failed, using fallback digest: %s", exc)
        return Digest(entries=tuple(self._fallback(c) for c in clusters))

    def _render(self, clusters: list[Cluster]) -> str:
        blocks = []
        for ci, c in enumerate(clusters):
            srcs = "; ".join(
                f"{p.article.title} ({p.article.url}) — {p.summary}" for p in c.items
            )
            blocks.append(f"Cluster {ci} [{c.topic}]: {srcs}")
        return "\n".join(blocks)

    def _entry(self, obj: dict) -> DigestEntry:
        importance = obj.get("importance", 3)
        try:
            importance = max(1, min(5, int(importance)))
        except (TypeError, ValueError):
            importance = 3
        return DigestEntry(
            title=str(obj.get("title", "Untitled")),
            category=str(obj.get("category", "Industry")),
            summary=str(obj.get("summary", "")),
            importance=importance,
            sources=tuple(str(s) for s in obj.get("sources", []) if s),
            tags=tuple(str(t) for t in obj.get("tags", []) if t),
        )

    def _fallback(self, cluster: Cluster) -> DigestEntry:
        first = cluster.items[0]
        return DigestEntry(
            title=cluster.topic,
            category=first.category,
            summary=" ".join(p.summary for p in cluster.items),
            importance=3,
            sources=tuple(p.article.url for p in cluster.items),
            tags=first.tags,
        )
```

- [ ] **Step 4: Run → pass** (3 passed). **Step 5: Commit** `feat: Analyst (smart-tier digest synthesis, tolerant)`.

---

## Task 6: Full suite check
- [ ] Run `uv run pytest -v`. Expect green (M1 15 + M2 22 + M3 18 = 55 passed). No commit if already committed per task.

## Done criteria for Milestone 3
- `extract_json`, processing data types, Processor, Clusterer, Analyst implemented + tested with mock Router.
- Every agent degrades gracefully on bad model output (never aborts the run).
- `uv run pytest` green; all committed.

**Next:** Milestone 4 (Content) — Writer + Translator + Quality Gate turn the `Digest` into publishable EN/VI Markdown.
