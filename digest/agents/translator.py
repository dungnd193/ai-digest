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

_SHORT = """Translate this blog {kind} into Vietnamese (tiếng Việt) ONLY.
Do NOT output French, Japanese, English, or any language other than Vietnamese.
Keep technical terms in English (e.g. "multi-agent", "LLM", "fine-tune").
Return ONLY the translated {kind} — no quotes, no labels, no explanation.

{kind}: {text}
"""


class Translator:
    """Translates an English BlogPost to Vietnamese per the configured mode.

    The article *body* is translated according to ``mode``:
      - ``gemma_only``     : 1 cheap call.
      - ``claude_only``    : 1 smart call.
      - ``draft_then_review`` (default): 1 cheap draft + 1 smart review.

    The short metadata fields (``title`` and, if present, ``summary``) are each
    translated with a single dedicated call. They use the smart tier in every
    mode except ``gemma_only`` (cheap), because the weak local model drifts to
    the wrong language on short prompts. Total call counts are unchanged:

      | mode              | empty summary | non-empty summary |
      |-------------------|---------------|-------------------|
      | gemma_only        | 2 (body+title)| 3 (+summary)      |
      | claude_only       | 2 (body+title)| 3 (+summary)      |
      | draft_then_review | 3 (body x2+ti)| 4 (+summary)      |
    """

    def __init__(self, router: Router, mode: str = "draft_then_review") -> None:
        self.router = router
        self.mode = mode

    def translate(self, post: BlogPost) -> BlogPost:
        # Short fields drift to the wrong language on the weak local model, so
        # use the smart tier for them in every mode except gemma_only.
        short_tier = "cheap" if self.mode == "gemma_only" else "smart"
        body = self._translate_text(post.body)
        title = self.router.run(
            _SHORT.format(kind="title", text=post.title), tier=short_tier
        ).strip()
        summary = (
            self.router.run(
                _SHORT.format(kind="summary", text=post.summary), tier=short_tier
            ).strip()
            if post.summary
            else ""
        )
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
        # draft_then_review: if the weak local model produced an empty/truncated
        # draft, reviewing it makes the smart model reply "no content to improve".
        # Fall back to a full smart translation of the original instead.
        if len(draft) < max(20, int(len(text) * 0.2)):
            return self.router.run(_DRAFT.format(body=text), tier="smart").strip()
        return self.router.run(_REVIEW.format(draft=draft), tier="smart").strip()
