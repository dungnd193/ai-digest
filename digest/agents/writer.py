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


_PREAMBLE_RE = re.compile(
    r"(?i)^(here'?s|here is|sure|okay|ok|below|i'?ll|certainly|this is)\b.*:\s*$"
)


def _clean_body(text: str) -> str:
    """Strip model chatter the prompt asked it not to emit: a wrapping code
    fence, a leading 'Here's the article:' preamble, and leading rules/blanks."""
    t = text.strip()
    # unwrap a single ```...``` fence around the whole body
    if t.startswith("```"):
        lines = t.split("\n")[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    # drop leading blank lines, horizontal rules, and a preamble line
    lines = t.split("\n")
    while lines:
        first = lines[0].strip()
        if first == "" or first == "---":
            lines.pop(0)
            continue
        if len(first) < 80 and _PREAMBLE_RE.match(first):
            lines.pop(0)
            continue
        break
    return "\n".join(lines).strip()


_PROMPT = """Write an engaging technical blog article in English Markdown about
the topic below, for readers who already know AI/tech. Use only standard
CommonMark (headings, lists, code fences, links). Do NOT use any template
shortcodes. Do NOT invent facts beyond the provided synthesis.

Base EVERY claim strictly on the synthesis below. Do NOT introduce specific
names, numbers, dates, allegations, quotes, or events that are not in the
synthesis. If the synthesis is thin, keep the article general and analytical
rather than inventing concrete details. Do not speculate as if it were fact.

Output ONLY the article body. Start directly with the first sentence or heading.
Do NOT add any preamble such as "Here's the article", do NOT wrap the output in
code fences, and do NOT include front-matter or a top-level title heading.

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
        body = _clean_body(_strip_shortcodes(raw))
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
