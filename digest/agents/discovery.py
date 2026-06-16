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
