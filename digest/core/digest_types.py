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
