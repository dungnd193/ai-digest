from __future__ import annotations

import logging
import re

from digest.core.content_types import BlogPost, slugify
from digest.core.digest_types import Digest, DigestEntry
from digest.core.router import Router

logger = logging.getLogger(__name__)

_SHORTCODE_RE = re.compile(r"\{\{(?:<.*?>|%.*?%)\}\}", re.DOTALL)


def _strip_shortcodes(text: str) -> str:
    """Remove Hugo shortcodes, looping to handle nested occurrences."""
    while True:
        stripped = _SHORTCODE_RE.sub("", text)
        if stripped == text:
            return stripped
        text = stripped

_PROMPT = """Write an engaging technical blog article in English Markdown about
the topic below, for readers who already know AI/tech. Use only standard
CommonMark (headings, lists, code fences, links). Do NOT use any template
shortcodes. Do NOT invent facts beyond the provided synthesis. Return only the
article body (no front-matter, no title heading).

Topic: {title}
Synthesis: {summary}
"""


class Writer:
    """Writes one English BlogPost per digest entry (smart tier)."""

    def __init__(self, router: Router) -> None:
        self.router = router

    def write(self, digest: Digest, *, date: str) -> list[BlogPost]:
        posts: list[BlogPost] = []
        for entry in digest.entries:
            try:
                posts.append(self._write_one(entry, date))
            except Exception as exc:  # noqa: BLE001 - one failure shouldn't abort
                logger.warning("writing failed for %r: %s", entry.title, exc)
        return posts

    def _write_one(self, entry: DigestEntry, date: str) -> BlogPost:
        raw = self.router.run(
            _PROMPT.format(title=entry.title, summary=entry.summary), tier="smart"
        )
        body = _strip_shortcodes(raw).strip()
        body += "\n\n## Sources\n" + "\n".join(f"- {u}" for u in entry.sources)
        return BlogPost(
            lang="en",
            title=entry.title,
            slug=slugify(entry.title),
            date=date,
            category=entry.category,
            tags=entry.tags,
            summary=entry.summary,
            body=body,
            sources=entry.sources,
        )
