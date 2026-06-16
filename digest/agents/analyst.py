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
            if not isinstance(data, list):
                raise TypeError("expected a JSON array of entries")
            entries = tuple(self._entry(obj) for obj in data if isinstance(obj, dict))
            if entries:
                return Digest(entries=entries)
        except (JSONExtractError, ValueError, TypeError, KeyError, AttributeError) as exc:
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
