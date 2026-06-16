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
