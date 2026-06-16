from __future__ import annotations

from digest.core.content_types import BlogPost
from digest.core.router import Router

_DRAFT = """Translate the following English blog content to Vietnamese for a
Vietnamese audience that knows AI. KEEP technical terms in English (do not
translate jargon like "multi-agent", "embedding", "prompt"). Preserve Markdown
structure and all URLs unchanged. Return only the translated content.

{body}
"""

_REVIEW = """You are a Vietnamese technical editor. Improve this machine
translation for fluency and correctness. KEEP technical terms in English and
keep all Markdown and URLs unchanged. Return only the improved content.

{draft}
"""

_TITLE = """Translate this blog title to Vietnamese, keeping technical terms in
English. Return only the translated title.

{title}
"""


class Translator:
    """Translates an English BlogPost to Vietnamese per the configured mode."""

    def __init__(self, router: Router, mode: str = "draft_then_review") -> None:
        self.router = router
        self.mode = mode

    def translate(self, post: BlogPost) -> BlogPost:
        body = self._translate_text(post.body)
        title = self.router.run(
            _TITLE.format(title=post.title),
            tier="smart" if self.mode == "claude_only" else "cheap",
        ).strip()
        summary = self._translate_text(post.summary) if post.summary else ""
        return BlogPost(
            lang="vi",
            title=title,
            slug=post.slug,
            date=post.date,
            category=post.category,
            tags=post.tags,
            summary=summary,
            body=body,
            sources=post.sources,
        )

    def _translate_text(self, text: str) -> str:
        if self.mode == "claude_only":
            return self.router.run(_DRAFT.format(body=text), tier="smart").strip()
        draft = self.router.run(_DRAFT.format(body=text), tier="cheap").strip()
        if self.mode == "gemma_only":
            return draft
        # draft_then_review
        return self.router.run(_REVIEW.format(draft=draft), tier="smart").strip()
