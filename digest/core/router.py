from __future__ import annotations

import os
import time

from digest.core.backends import Backend, BackendError, ClaudeBackend, OllamaBackend

CHEAP = "cheap"
SMART = "smart"


class Router:
    """Routes a task to a backend by tier, with bounded retry/backoff.

    Callers declare WHAT they need ("cheap" or "smart"), never which provider.
    This is the reusable seam: swapping Gemma/Claude/another model is a
    construction-time change, invisible to every agent.
    """

    def __init__(
        self,
        cheap: Backend,
        smart: Backend,
        retries: int = 2,
        backoff_base: float = 1.0,
    ) -> None:
        if retries < 0:
            raise ValueError(f"retries must be >= 0, got {retries!r}")
        self._backends = {CHEAP: cheap, SMART: smart}
        self.retries = retries
        self.backoff_base = backoff_base

    def run(self, task: str, tier: str, *, system: str | None = None) -> str:
        if tier not in self._backends:
            raise ValueError(f"unknown tier: {tier!r} (expected 'cheap' or 'smart')")
        backend = self._backends[tier]

        last_error: BackendError | None = None
        for attempt in range(self.retries + 1):
            try:
                return backend.generate(task, system=system)
            except BackendError as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(self.backoff_base * (2**attempt))
        if last_error is None:  # unreachable when retries >= 0
            raise RuntimeError("router exhausted attempts without an error")
        raise last_error


def build_router() -> "Router":
    """Construct the default Router from environment variables.

    Reads OLLAMA_BASE_URL, OLLAMA_MODEL, CLAUDE_BIN. Call load_env() first
    if you need a .env file loaded into the environment.
    """
    cheap = OllamaBackend(
        base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.environ.get("OLLAMA_MODEL", "gemma3:4b"),
    )
    smart = ClaudeBackend(claude_bin=os.environ.get("CLAUDE_BIN", "claude"))
    return Router(cheap=cheap, smart=smart)
