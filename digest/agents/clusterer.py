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
