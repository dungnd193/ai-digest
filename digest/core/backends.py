from __future__ import annotations

import subprocess
from typing import Protocol

import requests


class BackendError(RuntimeError):
    """Raised when a model backend fails to produce output."""


class Backend(Protocol):
    def generate(self, prompt: str, *, system: str | None = None) -> str: ...


class OllamaBackend:
    """Cheap tier — calls a local Ollama server via its HTTP API."""

    def __init__(self, base_url: str, model: str, timeout: int = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        if system is not None:
            payload["system"] = system
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()["response"]
        except Exception as exc:  # noqa: BLE001 - normalize to BackendError
            raise BackendError(f"Ollama generate failed: {exc}") from exc


class ClaudeBackend:
    """Smart tier — invokes the `claude` CLI headlessly (`claude -p`).

    Uses the Claude Max subscription via the CLI; no API key. One call =
    one high-quality reasoning pass. Retry/backoff is the Router's job.
    """

    def __init__(self, claude_bin: str = "claude", timeout: int = 180) -> None:
        self.claude_bin = claude_bin
        self.timeout = timeout

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        cmd = [self.claude_bin, "-p", prompt]
        if system is not None:
            cmd += ["--append-system-prompt", system]
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise BackendError(f"claude -p timed out after {self.timeout}s") from exc
        except Exception as exc:  # noqa: BLE001
            raise BackendError(f"claude -p failed to launch: {exc}") from exc

        if completed.returncode != 0:
            raise BackendError(
                f"claude -p exited {completed.returncode}: {completed.stderr.strip()}"
            )
        return completed.stdout.strip()
