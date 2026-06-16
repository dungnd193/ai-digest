from __future__ import annotations

import re
from dataclasses import dataclass


def slugify(title: str) -> str:
    """URL-safe ASCII slug: lowercase, non-alphanumerics become single hyphens.

    Non-ASCII characters (e.g. Vietnamese diacritics) collapse to hyphens, so
    callers needing a meaningful slug for non-ASCII titles should pass an
    ASCII source. Falls back to ``"post"`` when nothing slug-able remains.
    """
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "post"


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
