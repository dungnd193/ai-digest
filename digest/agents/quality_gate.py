from __future__ import annotations

import logging

from digest.core.content_types import BlogPost, QualityVerdict
from digest.core.jsonutil import JSONExtractError, extract_json
from digest.core.router import Router

logger = logging.getLogger(__name__)

_PROMPT = """Review this blog post for factual grounding. Does it avoid
fabricated claims and stay consistent with its listed sources? Return ONLY JSON:
{{"pass": true/false, "reason": "short explanation"}}

Title: {title}
Sources: {sources}
Body:
{body}
"""


class QualityGate:
    """Flags fabricated/ungrounded posts before publish (smart tier).
    Fail-open on its own errors — human approval is the early backstop."""

    def __init__(self, router: Router) -> None:
        self.router = router

    def check(self, post: BlogPost) -> QualityVerdict:
        prompt = _PROMPT.format(
            title=post.title,
            sources=", ".join(post.sources),
            body=post.body[:4000],
        )
        try:
            raw = self.router.run(prompt, tier="smart")
            data = extract_json(raw)
            if not isinstance(data, dict) or "pass" not in data:
                raise JSONExtractError("missing 'pass'")
            return QualityVerdict(
                passed=bool(data["pass"]),
                reason=str(data.get("reason", "")),
            )
        except (JSONExtractError, ValueError, TypeError) as exc:
            logger.warning("quality gate inconclusive for %r: %s", post.title, exc)
            return QualityVerdict(passed=True, reason="gate inconclusive")
        except Exception as exc:  # noqa: BLE001 - model/transport failure
            logger.warning("quality gate error for %r: %s", post.title, exc)
            return QualityVerdict(passed=True, reason="gate inconclusive")
