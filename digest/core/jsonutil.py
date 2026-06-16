from __future__ import annotations

import json
from typing import Any


class JSONExtractError(ValueError):
    """Raised when no parseable JSON value can be found in model output."""


def extract_json(text: str) -> Any:
    """Best-effort parse of a JSON value embedded in LLM text.

    Tries the whole string, then strips code fences, then falls back to the
    substring spanning the first opening bracket to the last matching closing
    bracket. Raises JSONExtractError if nothing parses.
    """
    candidates: list[str] = [text.strip()]

    fenced = text.replace("```json", "```")
    if "```" in fenced:
        parts = fenced.split("```")
        candidates.extend(p.strip() for p in parts if p.strip())

    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        end = text.rfind(closer)
        if start != -1 and end != -1 and end > start:
            candidates.append(text[start : end + 1])

    for cand in candidates:
        try:
            return json.loads(cand)
        except (json.JSONDecodeError, ValueError):
            continue
    raise JSONExtractError(f"no JSON found in: {text[:120]!r}")
