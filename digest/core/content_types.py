from __future__ import annotations

import re
from dataclasses import dataclass


def slugify(title: str) -> str:
    """URL-safe slug: lowercase, non-alphanumerics become single hyphens."""
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


@dataclass(frozen=True)
class BlogPost:
    """Generator-neutral blog post. `body` is plain CommonMark — NO Hugo
    shortcodes — so the static-site generator can be swapped without rework."""

    lang: str
    title: str
    slug: str
    date: str
    category: str
    tags: tuple[str, ...]
    summary: str
    body: str
    sources: tuple[str, ...]


@dataclass(frozen=True)
class QualityVerdict:
    passed: bool
    reason: str
