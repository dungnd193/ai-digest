# Milestone 2: Ingestion — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax. Follow TDD: failing test → run (fail) → minimal code → run (pass) → commit.

**Goal:** Gather candidate articles from two sources — RSS feeds (Collector) and daily web search (Discovery via Tavily) — deduplicate them, and filter out anything already processed (SeenStore), returning a list of fresh `Article` objects.

**Architecture:** A minimal immutable `Article` value type is the unit that flows through the whole pipeline. `Collector` parses RSS feeds (tolerant: one broken feed never breaks the run). `Discovery` queries a `Searcher` (Tavily behind an interface, mirroring the Model Router seam) and optionally drops irrelevant hits using the cheap model tier. `SeenStore` persists processed IDs to JSON for idempotency. An `Ingestor` wires these together. No model calls are required for the happy path except optional relevance filtering.

**Tech Stack:** Python 3.14, `uv`, `pytest`, `feedparser` (RSS), `requests` (Tavily HTTP). Reuses `digest.core.router.Router` from Milestone 1.

---

## Conventions
- Repo root: `~/Desktop/Workspace/ai-digest`, branch `feat/milestones`.
- `export PATH="$HOME/.local/bin:$PATH"` before any `uv` command.
- Run tests: `uv run pytest <path> -v`.
- Commit after each task with trailer:
  ```
  Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
  ```
- All tests use mocks — NO real network (no real feeds, no real Tavily).

## Add dependencies (once, before Task 1)
```bash
cd ~/Desktop/Workspace/ai-digest && export PATH="$HOME/.local/bin:$PATH"
uv add feedparser
```
(`requests` already added in Milestone 1.)

## File structure (created by this milestone)
```
digest/
├── core/
│   ├── models.py        # Article value type + make_id
│   ├── state.py         # SeenStore (JSON persistence)
│   └── search.py        # SearchResult, Searcher protocol, TavilyBackend, build_searcher
├── agents/
│   ├── __init__.py
│   ├── collector.py     # Collector (RSS via feedparser)
│   ├── discovery.py     # Discovery (search + optional relevance filter)
│   └── ingestor.py      # Ingestor (combine + dedupe + filter_new)
├── config/
│   └── feeds.yaml       # RSS feed urls + topics
└── tests/
    ├── test_models.py  test_state.py  test_search.py
    ├── test_collector.py  test_discovery.py  test_ingestor.py
```

Responsibility boundaries: `models` = data only; `collector`/`discovery` = produce Articles from one source each; `state` = persistence; `ingestor` = orchestrate the three. Each is independently testable with mocks.

---

## Task 1: Article value type

**Files:** Create `digest/core/models.py`; Test `digest/tests/test_models.py`

- [ ] **Step 1: Write failing tests**

`digest/tests/test_models.py`:
```python
from digest.core.models import Article, make_id


def test_make_id_is_stable_and_short():
    a = make_id("https://example.com/post")
    b = make_id("https://example.com/post")
    assert a == b
    assert len(a) == 16


def test_make_id_differs_by_url():
    assert make_id("https://a.com") != make_id("https://b.com")


def test_article_create_derives_id_from_url():
    art = Article.create(url="https://x.com/p", title="T", source="Feed")
    assert art.id == make_id("https://x.com/p")
    assert art.title == "T"
    assert art.source == "Feed"
    assert art.published == ""
    assert art.content == ""


def test_article_is_frozen_hashable():
    art = Article.create(url="https://x.com/p", title="T", source="F")
    {art}  # hashable -> no error
```

- [ ] **Step 2: Run → fail** (`uv run pytest digest/tests/test_models.py -v`), expect ModuleNotFoundError.

- [ ] **Step 3: Implement** `digest/core/models.py`:
```python
from __future__ import annotations

import hashlib
from dataclasses import dataclass


def make_id(url: str) -> str:
    """Stable 16-char id derived from the article URL (used for dedupe + seen)."""
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class Article:
    """Immutable ingestion unit flowing through the pipeline.

    Enrichment (summary, category, tags) is added by later milestones as
    separate types; this stays minimal so the ingestion contract is stable.
    """

    id: str
    url: str
    title: str
    source: str
    published: str = ""
    content: str = ""

    @classmethod
    def create(
        cls,
        *,
        url: str,
        title: str,
        source: str,
        published: str = "",
        content: str = "",
    ) -> "Article":
        return cls(
            id=make_id(url),
            url=url,
            title=title,
            source=source,
            published=published,
            content=content,
        )
```

- [ ] **Step 4: Run → pass** (4 passed). **Step 5: Commit** `feat: Article value type + make_id`.

---

## Task 2: SeenStore

**Files:** Create `digest/core/state.py`; Test `digest/tests/test_state.py`

- [ ] **Step 1: Write failing tests**

`digest/tests/test_state.py`:
```python
from digest.core.models import Article
from digest.core.state import SeenStore


def test_seenstore_empty_when_no_file(tmp_path):
    store = SeenStore(tmp_path / "seen.json")
    assert store.has("abc") is False


def test_seenstore_add_and_has(tmp_path):
    store = SeenStore(tmp_path / "seen.json")
    store.add("abc")
    assert store.has("abc") is True


def test_seenstore_persists_across_instances(tmp_path):
    path = tmp_path / "seen.json"
    s1 = SeenStore(path)
    s1.add("x")
    s1.save()
    s2 = SeenStore(path)
    assert s2.has("x") is True


def test_filter_new_returns_only_unseen(tmp_path):
    store = SeenStore(tmp_path / "seen.json")
    a = Article.create(url="https://a.com", title="A", source="F")
    b = Article.create(url="https://b.com", title="B", source="F")
    store.add(a.id)
    new = store.filter_new([a, b])
    assert new == [b]
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/core/state.py`:
```python
from __future__ import annotations

import json
from pathlib import Path

from digest.core.models import Article


class SeenStore:
    """Tracks processed article ids for idempotency. JSON-backed.

    Call add()/add_many() then save() to persist. Marking-as-seen is the
    caller's decision (typically after successful publish), so loading and
    filtering never mutate state on disk.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._ids: set[str] = set()
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as fh:
                self._ids = set(json.load(fh))

    def has(self, article_id: str) -> bool:
        return article_id in self._ids

    def add(self, article_id: str) -> None:
        self._ids.add(article_id)

    def add_many(self, ids: list[str]) -> None:
        self._ids.update(ids)

    def filter_new(self, articles: list[Article]) -> list[Article]:
        return [a for a in articles if a.id not in self._ids]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(sorted(self._ids), fh, indent=2)
```

- [ ] **Step 4: Run → pass** (4 passed). **Step 5: Commit** `feat: SeenStore for idempotent dedupe`.

---

## Task 3: Search interface + Tavily backend

**Files:** Create `digest/core/search.py`; Test `digest/tests/test_search.py`

- [ ] **Step 1: Write failing tests**

`digest/tests/test_search.py`:
```python
from unittest.mock import MagicMock, patch

import pytest

from digest.core.search import SearchError, SearchResult, TavilyBackend


def test_tavily_search_returns_results():
    fake = MagicMock()
    fake.raise_for_status.return_value = None
    fake.json.return_value = {
        "results": [
            {"url": "https://a.com", "title": "A", "content": "ca"},
            {"url": "https://b.com", "title": "B", "content": "cb"},
        ]
    }
    with patch("digest.core.search.requests.post", return_value=fake) as post:
        be = TavilyBackend(api_key="k")
        out = be.search("ai agents", max_results=2)

    assert out == [
        SearchResult(url="https://a.com", title="A", content="ca"),
        SearchResult(url="https://b.com", title="B", content="cb"),
    ]
    payload = post.call_args.kwargs["json"]
    assert payload["query"] == "ai agents"
    assert payload["max_results"] == 2
    assert payload["api_key"] == "k"


def test_tavily_search_raises_searcherror_on_http_failure():
    with patch("digest.core.search.requests.post", side_effect=Exception("boom")):
        be = TavilyBackend(api_key="k")
        with pytest.raises(SearchError):
            be.search("x")


def test_tavily_search_tolerates_missing_fields():
    fake = MagicMock()
    fake.raise_for_status.return_value = None
    fake.json.return_value = {"results": [{"url": "https://a.com"}]}
    with patch("digest.core.search.requests.post", return_value=fake):
        be = TavilyBackend(api_key="k")
        out = be.search("x")
    assert out == [SearchResult(url="https://a.com", title="", content="")]
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/core/search.py`:
```python
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

import requests


class SearchError(RuntimeError):
    """Raised when a search backend fails."""


@dataclass(frozen=True)
class SearchResult:
    url: str
    title: str = ""
    content: str = ""


class Searcher(Protocol):
    def search(self, query: str, *, max_results: int = 5) -> list[SearchResult]: ...


class TavilyBackend:
    """Search via the Tavily API. Wrapped behind Searcher so the backend is
    swappable (mirrors the Model Router seam)."""

    ENDPOINT = "https://api.tavily.com/search"

    def __init__(self, api_key: str, timeout: int = 30) -> None:
        self.api_key = api_key
        self.timeout = timeout

    def search(self, query: str, *, max_results: int = 5) -> list[SearchResult]:
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
        }
        try:
            resp = requests.post(self.ENDPOINT, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            raise SearchError(f"Tavily search failed: {exc}") from exc

        return [
            SearchResult(
                url=r["url"],
                title=r.get("title", ""),
                content=r.get("content", ""),
            )
            for r in data.get("results", [])
        ]


def build_searcher() -> Searcher:
    """Construct the default searcher from TAVILY_API_KEY."""
    return TavilyBackend(api_key=os.environ.get("TAVILY_API_KEY", ""))
```

- [ ] **Step 4: Run → pass** (3 passed). **Step 5: Commit** `feat: Tavily search backend behind Searcher interface`.

---

## Task 4: Collector (RSS)

**Files:** Create `digest/agents/__init__.py`, `digest/agents/collector.py`, `digest/config/feeds.yaml`; Test `digest/tests/test_collector.py`

- [ ] **Step 1: Create `digest/config/feeds.yaml`**
```yaml
feeds:
  - https://hnrss.org/frontpage
  - https://feeds.arstechnica.com/arstechnica/index
topics: ["AI", "machine learning", "agents", "software"]
```

- [ ] **Step 2: Write failing tests**

`digest/tests/test_collector.py`:
```python
from types import SimpleNamespace
from unittest.mock import patch

from digest.agents.collector import Collector
from digest.core.models import make_id


def _feed(title, entries):
    return SimpleNamespace(feed=SimpleNamespace(title=title), entries=entries, bozo=0)


def _entry(link, title, summary="", published=""):
    return {"link": link, "title": title, "summary": summary, "published": published}


def test_collector_parses_entries_into_articles():
    parsed = _feed("My Feed", [_entry("https://a.com/1", "First", "body", "2026-06-16")])
    with patch("digest.agents.collector.feedparser.parse", return_value=parsed):
        arts = Collector(["http://feed"]).collect()
    assert len(arts) == 1
    assert arts[0].id == make_id("https://a.com/1")
    assert arts[0].title == "First"
    assert arts[0].source == "My Feed"
    assert arts[0].content == "body"
    assert arts[0].published == "2026-06-16"


def test_collector_skips_broken_feed_and_continues():
    good = _feed("Good", [_entry("https://a.com/1", "ok")])

    def fake_parse(url):
        if url == "bad":
            raise Exception("network down")
        return good

    with patch("digest.agents.collector.feedparser.parse", side_effect=fake_parse):
        arts = Collector(["bad", "good"]).collect()
    assert len(arts) == 1
    assert arts[0].title == "ok"


def test_collector_skips_entries_without_link():
    parsed = _feed("F", [{"title": "no link"}, _entry("https://a.com/1", "has link")])
    with patch("digest.agents.collector.feedparser.parse", return_value=parsed):
        arts = Collector(["http://feed"]).collect()
    assert [a.title for a in arts] == ["has link"]
```

- [ ] **Step 3: Run → fail.**

- [ ] **Step 4: Implement** `digest/agents/__init__.py` (empty) and `digest/agents/collector.py`:
```python
from __future__ import annotations

import logging

import feedparser

from digest.core.models import Article

logger = logging.getLogger(__name__)


class Collector:
    """Fetches RSS/Atom feeds and yields Articles. Tolerant: a failing feed
    is logged and skipped so one bad source never breaks the run."""

    def __init__(self, feed_urls: list[str]) -> None:
        self.feed_urls = feed_urls

    def collect(self) -> list[Article]:
        articles: list[Article] = []
        for url in self.feed_urls:
            try:
                parsed = feedparser.parse(url)
            except Exception as exc:  # noqa: BLE001
                logger.warning("feed failed: %s (%s)", url, exc)
                continue
            source = getattr(parsed.feed, "title", url)
            for entry in parsed.entries:
                link = entry.get("link")
                if not link:
                    continue
                articles.append(
                    Article.create(
                        url=link,
                        title=entry.get("title", ""),
                        source=source,
                        published=entry.get("published", ""),
                        content=entry.get("summary", ""),
                    )
                )
        return articles
```

- [ ] **Step 5: Run → pass** (3 passed). **Step 6: Commit** `feat: RSS Collector (tolerant per-feed)`.

---

## Task 5: Discovery (search + optional relevance filter)

**Files:** Create `digest/agents/discovery.py`; Test `digest/tests/test_discovery.py`

- [ ] **Step 1: Write failing tests**

`digest/tests/test_discovery.py`:
```python
from unittest.mock import MagicMock

from digest.agents.discovery import Discovery
from digest.core.search import SearchError, SearchResult


def _searcher(mapping):
    s = MagicMock()
    s.search.side_effect = lambda q, max_results=5: mapping[q]
    return s


def test_discovery_converts_results_to_articles():
    s = _searcher({"ai": [SearchResult(url="https://a.com", title="A", content="c")]})
    arts = Discovery(searcher=s).discover(["ai"])
    assert len(arts) == 1
    assert arts[0].url == "https://a.com"
    assert arts[0].source == "discovery:ai"
    assert arts[0].content == "c"


def test_discovery_dedupes_across_keywords():
    r = SearchResult(url="https://dup.com", title="D", content="c")
    s = _searcher({"k1": [r], "k2": [r]})
    arts = Discovery(searcher=s).discover(["k1", "k2"])
    assert len(arts) == 1


def test_discovery_skips_keyword_on_search_error():
    s = MagicMock()
    s.search.side_effect = SearchError("boom")
    arts = Discovery(searcher=s).discover(["k1"])
    assert arts == []


def test_discovery_relevance_filter_drops_no_answers():
    s = _searcher({"ai": [
        SearchResult(url="https://yes.com", title="Y", content="relevant"),
        SearchResult(url="https://no.com", title="N", content="spam"),
    ]})
    router = MagicMock()
    # cheap model says yes for the first, no for the second
    router.run.side_effect = ["YES", "no, unrelated"]
    arts = Discovery(searcher=s, router=router).discover(["ai"])
    assert [a.url for a in arts] == ["https://yes.com"]
    assert router.run.call_count == 2
    assert router.run.call_args_list[0].kwargs["tier"] == "cheap"
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/agents/discovery.py`:
```python
from __future__ import annotations

import logging

from digest.core.models import Article
from digest.core.router import Router
from digest.core.search import SearchError, Searcher

logger = logging.getLogger(__name__)


class Discovery:
    """Finds fresh articles via daily web search. Tolerant per keyword.

    If a Router is supplied, each candidate is scored for relevance by the
    cheap model tier and irrelevant hits are dropped before they cost
    downstream work.
    """

    def __init__(
        self,
        searcher: Searcher,
        router: Router | None = None,
        max_results: int = 5,
    ) -> None:
        self.searcher = searcher
        self.router = router
        self.max_results = max_results

    def discover(self, keywords: list[str]) -> list[Article]:
        articles: list[Article] = []
        seen_urls: set[str] = set()
        for kw in keywords:
            try:
                results = self.searcher.search(kw, max_results=self.max_results)
            except SearchError as exc:
                logger.warning("discovery search failed for %r: %s", kw, exc)
                continue
            for r in results:
                if r.url in seen_urls:
                    continue
                if self.router is not None and not self._is_relevant(r, kw):
                    continue
                seen_urls.add(r.url)
                articles.append(
                    Article.create(
                        url=r.url,
                        title=r.title,
                        source=f"discovery:{kw}",
                        content=r.content,
                    )
                )
        return articles

    def _is_relevant(self, result, keyword: str) -> bool:
        prompt = (
            f"Topic: {keyword}\n"
            f"Title: {result.title}\n"
            f"Excerpt: {result.content[:500]}\n\n"
            "Is this article relevant to the topic? Answer with only YES or NO."
        )
        try:
            answer = self.router.run(prompt, tier="cheap")
        except Exception as exc:  # noqa: BLE001 - be permissive on filter failure
            logger.warning("relevance check failed, keeping article: %s", exc)
            return True
        return answer.strip().upper().startswith("YES")
```

- [ ] **Step 4: Run → pass** (4 passed). **Step 5: Commit** `feat: Discovery agent (search + relevance filter)`.

---

## Task 6: Ingestor (combine + dedupe + filter_new)

**Files:** Create `digest/agents/ingestor.py`; Test `digest/tests/test_ingestor.py`

- [ ] **Step 1: Write failing tests**

`digest/tests/test_ingestor.py`:
```python
from unittest.mock import MagicMock

from digest.agents.ingestor import Ingestor
from digest.core.models import Article


def _art(url, title="T"):
    return Article.create(url=url, title=title, source="S")


def test_ingestor_combines_collector_and_discovery():
    collector = MagicMock()
    collector.collect.return_value = [_art("https://a.com")]
    discovery = MagicMock()
    discovery.discover.return_value = [_art("https://b.com")]
    seen = MagicMock()
    seen.filter_new.side_effect = lambda arts: arts

    out = Ingestor(collector, discovery, seen).gather(keywords=["k"])
    assert {a.url for a in out} == {"https://a.com", "https://b.com"}


def test_ingestor_dedupes_same_url_from_both_sources():
    collector = MagicMock()
    collector.collect.return_value = [_art("https://dup.com")]
    discovery = MagicMock()
    discovery.discover.return_value = [_art("https://dup.com")]
    seen = MagicMock()
    seen.filter_new.side_effect = lambda arts: arts

    out = Ingestor(collector, discovery, seen).gather(keywords=["k"])
    assert len(out) == 1


def test_ingestor_filters_already_seen():
    a, b = _art("https://a.com"), _art("https://b.com")
    collector = MagicMock()
    collector.collect.return_value = [a, b]
    discovery = MagicMock()
    discovery.discover.return_value = []
    seen = MagicMock()
    seen.filter_new.return_value = [b]  # a already seen

    out = Ingestor(collector, discovery, seen).gather(keywords=["k"])
    assert out == [b]


def test_ingestor_skips_discovery_when_disabled():
    collector = MagicMock()
    collector.collect.return_value = [_art("https://a.com")]
    discovery = MagicMock()
    seen = MagicMock()
    seen.filter_new.side_effect = lambda arts: arts

    out = Ingestor(collector, discovery, seen).gather(keywords=["k"], discovery_enabled=False)
    assert len(out) == 1
    discovery.discover.assert_not_called()
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/agents/ingestor.py`:
```python
from __future__ import annotations

from digest.agents.collector import Collector
from digest.agents.discovery import Discovery
from digest.core.models import Article
from digest.core.state import SeenStore


class Ingestor:
    """Combines Collector + Discovery, dedupes by article id, and returns
    only articles not already in the SeenStore. Does NOT mark anything seen
    (that happens after successful publish)."""

    def __init__(
        self,
        collector: Collector,
        discovery: Discovery,
        seen: SeenStore,
    ) -> None:
        self.collector = collector
        self.discovery = discovery
        self.seen = seen

    def gather(
        self,
        keywords: list[str],
        discovery_enabled: bool = True,
    ) -> list[Article]:
        items: list[Article] = list(self.collector.collect())
        if discovery_enabled:
            items += self.discovery.discover(keywords)

        deduped: dict[str, Article] = {}
        for art in items:
            deduped.setdefault(art.id, art)

        return self.seen.filter_new(list(deduped.values()))
```

- [ ] **Step 4: Run → pass** (4 passed). **Step 5: Commit** `feat: Ingestor combines sources, dedupes, filters seen`.

---

## Task 7: Full suite check

- [ ] **Step 1:** Run `uv run pytest -v`. Expect ALL green (Milestone 1's 15 + Milestone 2's 22 = 37 passed).
- [ ] **Step 2:** If green, no commit needed (already committed per task).

---

## Done criteria for Milestone 2
- `Article`, `make_id`, `SeenStore`, `SearchResult`/`Searcher`/`TavilyBackend`, `Collector`, `Discovery`, `Ingestor` all implemented and tested with mocks.
- One broken feed / failed search keyword never aborts the run.
- `uv run pytest` green.
- All work committed.

**Next:** Milestone 3 (Processing) — Processor + Clustering + Lead Analyst turn these raw Articles into a digest.
