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
            if getattr(parsed, "bozo", False):
                logger.warning("feed malformed/unreachable: %s (%s)", url, getattr(parsed, "bozo_exception", ""))
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
