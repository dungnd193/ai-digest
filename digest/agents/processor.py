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
        raw = self.router.run(prompt, tier="cheap", label=f"processor:{article.title[:30]}")
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
