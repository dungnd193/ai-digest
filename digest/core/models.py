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
