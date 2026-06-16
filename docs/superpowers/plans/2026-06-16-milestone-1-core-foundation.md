# Milestone 1: Core Foundation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the reusable core of AI Digest — a `Router.run(task, tier)` abstraction that routes "cheap" work to Gemma (Ollama HTTP) and "smart" work to Claude (`claude -p` subprocess), plus config loading from `.env` + `settings.yaml`.

**Architecture:** A thin `Backend` protocol with two implementations (`OllamaBackend`, `ClaudeBackend`). A `Router` holds one cheap + one smart backend and dispatches by `tier`, with bounded retry/backoff for the smart tier. Config is split: secrets/paths in `.env` (python-dotenv), behavior in `config/settings.yaml` (PyYAML). Every unit is a pure-ish class tested in isolation with mocks — no real network or subprocess calls in tests.

**Tech Stack:** Python 3.11+, `uv` (package manager), `pytest`, `requests` (Ollama HTTP), `python-dotenv`, `PyYAML`. Claude is invoked via the `claude` CLI as a subprocess (no API key).

---

## Conventions for this plan

- **Repo root:** `~/Desktop/Workspace/ai-digest`. All paths below are relative to it.
- **Python package:** `digest` (importable as `from digest.core.router import Router`).
- **Run tests** from repo root with: `uv run pytest <path> -v`.
- **Git identity** (run once if commits fail): `git config user.name "dungnd" && git config user.email "techx-ai-factory-3@techxcorp.com"`.
- **Commit message trailer:** append a blank line then `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` to each commit. Omitted from the short examples below for brevity — add it.
- **TDD:** every behavior gets a failing test first.

---

## File structure (created by this milestone)

```
ai-digest/
├── pyproject.toml                 # uv project + pytest config + deps
├── digest/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # load .env + settings.yaml
│   │   ├── backends.py            # Backend protocol + OllamaBackend + ClaudeBackend
│   │   └── router.py              # Router(cheap, smart).run(task, tier)
│   ├── config/
│   │   └── settings.yaml          # default behavior config
│   └── tests/
│       ├── __init__.py
│       ├── test_config.py
│       ├── test_backends.py
│       └── test_router.py
├── .env.example                   # template (real .env is gitignored)
```

Responsibilities:
- `config.py` — load and validate configuration; nothing else.
- `backends.py` — turn a prompt into text via one provider each; no routing logic.
- `router.py` — pick a backend by tier and apply retry; no provider details.

---

## Task 0: Project scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `digest/__init__.py`, `digest/core/__init__.py`, `digest/tests/__init__.py`
- Create: `.env.example`

- [ ] **Step 1: Initialize uv project and add dependencies**

Run from repo root:
```bash
cd ~/Desktop/Workspace/ai-digest
uv init --no-workspace --bare 2>/dev/null || true
uv add requests python-dotenv PyYAML
uv add --dev pytest
```

- [ ] **Step 2: Write `pyproject.toml` package + pytest config**

Ensure `pyproject.toml` contains (merge with what `uv init` generated; keep the `[project]` deps it created):

```toml
[tool.pytest.ini_options]
testpaths = ["digest/tests"]
addopts = "-ra"

[tool.setuptools.packages.find]
include = ["digest*"]
```

If `uv init --bare` did not create a build backend, add a `[build-system]` only if `uv run pytest` later fails to import `digest`. The package is imported via the repo-root being on `sys.path` (pytest rootdir), so a build backend is usually unnecessary.

- [ ] **Step 3: Create package directories and init files**

```bash
mkdir -p digest/core digest/config digest/tests
touch digest/__init__.py digest/core/__init__.py digest/tests/__init__.py
```

- [ ] **Step 4: Create `.env.example`**

Create `.env.example`:
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
CLAUDE_BIN=claude
TAVILY_API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

- [ ] **Step 5: Verify pytest runs (collects zero tests, no error)**

Run: `uv run pytest -q`
Expected: exits 0 with "no tests ran" (or collected 0 items). If it errors on import, fix before continuing.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml uv.lock digest/ .env.example
git commit -m "chore: scaffold digest package with uv + pytest"
```

---

## Task 1: Config loader

**Files:**
- Create: `digest/core/config.py`
- Create: `digest/config/settings.yaml`
- Test: `digest/tests/test_config.py`

- [ ] **Step 1: Write the default `settings.yaml`**

Create `digest/config/settings.yaml`:
```yaml
schedule: daily
languages: [en, vi]
vi_keep_english_terms: true
articles_per_run: 8
translator_mode: draft_then_review
approval_required: true
categories: [Research, Tools, Industry, Tutorial, Opinion]
discovery:
  enabled: true
  keywords: ["multi-agent LLM", "AI automation", "agentic workflows"]
steps:
  digest: true
  blog: true
  publish: true
notify:
  telegram_daily_summary: true
  telegram_error_alert: true
```

- [ ] **Step 2: Write the failing tests**

Create `digest/tests/test_config.py`:
```python
from pathlib import Path

import pytest

from digest.core.config import Settings, load_settings


def test_load_settings_reads_yaml(tmp_path):
    p = tmp_path / "settings.yaml"
    p.write_text("articles_per_run: 5\napproval_required: false\n")
    s = load_settings(p)
    assert s.articles_per_run == 5
    assert s.approval_required is False


def test_settings_exposes_nested_via_get(tmp_path):
    p = tmp_path / "settings.yaml"
    p.write_text("discovery:\n  enabled: true\n  keywords: [a, b]\n")
    s = load_settings(p)
    assert s.get("discovery.enabled") is True
    assert s.get("discovery.keywords") == ["a", "b"]


def test_settings_get_returns_default_for_missing(tmp_path):
    p = tmp_path / "settings.yaml"
    p.write_text("articles_per_run: 5\n")
    s = load_settings(p)
    assert s.get("nope.missing", "fallback") == "fallback"


def test_load_settings_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_settings(tmp_path / "absent.yaml")
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest digest/tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'digest.core.config'`.

- [ ] **Step 4: Implement `config.py`**

Create `digest/core/config.py`:
```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass
class Settings:
    """Behavior config loaded from settings.yaml. Attribute access for top-level
    keys; dotted .get() for nested values."""

    _data: dict[str, Any] = field(default_factory=dict)

    def __getattr__(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def get(self, dotted_key: str, default: Any = None) -> Any:
        node: Any = self._data
        for part in dotted_key.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node


def load_settings(path: str | Path) -> Settings:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"settings file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return Settings(_data=data)


def load_env(path: str | Path | None = None) -> None:
    """Load secrets/paths from a .env file into os.environ (no-op if absent)."""
    if path is None:
        load_dotenv()
    else:
        load_dotenv(dotenv_path=Path(path))
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest digest/tests/test_config.py -v`
Expected: PASS (4 passed).

- [ ] **Step 6: Commit**

```bash
git add digest/core/config.py digest/config/settings.yaml digest/tests/test_config.py
git commit -m "feat: config loader for settings.yaml + .env"
```

---

## Task 2: Ollama backend (cheap tier)

**Files:**
- Create: `digest/core/backends.py`
- Test: `digest/tests/test_backends.py`

- [ ] **Step 1: Write the failing tests**

Create `digest/tests/test_backends.py`:
```python
from unittest.mock import MagicMock, patch

import pytest

from digest.core.backends import (
    BackendError,
    ClaudeBackend,
    OllamaBackend,
)


def test_ollama_generate_posts_and_returns_response():
    fake_resp = MagicMock()
    fake_resp.json.return_value = {"response": "hello world"}
    fake_resp.raise_for_status.return_value = None

    with patch("digest.core.backends.requests.post", return_value=fake_resp) as post:
        be = OllamaBackend(base_url="http://x:11434", model="gemma3:4b")
        out = be.generate("hi", system="be brief")

    assert out == "hello world"
    args, kwargs = post.call_args
    assert kwargs["json"]["model"] == "gemma3:4b"
    assert kwargs["json"]["prompt"] == "hi"
    assert kwargs["json"]["system"] == "be brief"
    assert kwargs["json"]["stream"] is False


def test_ollama_generate_raises_backenderror_on_http_failure():
    with patch("digest.core.backends.requests.post", side_effect=Exception("boom")):
        be = OllamaBackend(base_url="http://x:11434", model="gemma3:4b")
        with pytest.raises(BackendError):
            be.generate("hi")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest digest/tests/test_backends.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'digest.core.backends'`.

- [ ] **Step 3: Implement the Ollama backend (and shared protocol/error)**

Create `digest/core/backends.py`:
```python
from __future__ import annotations

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest digest/tests/test_backends.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add digest/core/backends.py digest/tests/test_backends.py
git commit -m "feat: OllamaBackend (cheap tier) + Backend protocol"
```

---

## Task 3: Claude backend (smart tier)

**Files:**
- Modify: `digest/core/backends.py` (append `ClaudeBackend`)
- Test: `digest/tests/test_backends.py` (append tests)

- [ ] **Step 1: Write the failing tests**

Append to `digest/tests/test_backends.py`:
```python
def test_claude_generate_invokes_cli_and_returns_stdout():
    completed = MagicMock()
    completed.stdout = "claude says hi\n"
    completed.returncode = 0

    with patch("digest.core.backends.subprocess.run", return_value=completed) as run:
        be = ClaudeBackend(claude_bin="claude", timeout=60)
        out = be.generate("hi", system="be brief")

    assert out == "claude says hi"
    cmd = run.call_args.args[0]
    assert cmd[0] == "claude"
    assert "-p" in cmd
    # system prompt passed via --append-system-prompt
    assert "--append-system-prompt" in cmd
    assert "be brief" in cmd


def test_claude_generate_raises_backenderror_on_timeout():
    import subprocess as _sp

    with patch(
        "digest.core.backends.subprocess.run",
        side_effect=_sp.TimeoutExpired(cmd="claude", timeout=60),
    ):
        be = ClaudeBackend(claude_bin="claude", timeout=60)
        with pytest.raises(BackendError):
            be.generate("hi")


def test_claude_generate_raises_backenderror_on_nonzero_exit():
    completed = MagicMock()
    completed.stdout = ""
    completed.stderr = "quota exceeded"
    completed.returncode = 1

    with patch("digest.core.backends.subprocess.run", return_value=completed):
        be = ClaudeBackend(claude_bin="claude", timeout=60)
        with pytest.raises(BackendError):
            be.generate("hi")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest digest/tests/test_backends.py -v`
Expected: FAIL — `ImportError: cannot import name 'ClaudeBackend'`.

- [ ] **Step 3: Implement `ClaudeBackend`**

Add `import subprocess` to the top of `digest/core/backends.py` (alongside `import requests`), then append:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest digest/tests/test_backends.py -v`
Expected: PASS (5 passed total in this file).

- [ ] **Step 5: Commit**

```bash
git add digest/core/backends.py digest/tests/test_backends.py
git commit -m "feat: ClaudeBackend (smart tier) via claude -p subprocess"
```

---

## Task 4: Model Router

**Files:**
- Create: `digest/core/router.py`
- Test: `digest/tests/test_router.py`

- [ ] **Step 1: Write the failing tests**

Create `digest/tests/test_router.py`:
```python
from unittest.mock import MagicMock

import pytest

from digest.core.backends import BackendError
from digest.core.router import Router


def _backend(return_value=None, side_effect=None):
    be = MagicMock()
    be.generate.return_value = return_value
    if side_effect is not None:
        be.generate.side_effect = side_effect
    return be


def test_router_cheap_tier_calls_cheap_backend():
    cheap = _backend("cheap-out")
    smart = _backend("smart-out")
    r = Router(cheap=cheap, smart=smart)
    assert r.run("task", tier="cheap") == "cheap-out"
    cheap.generate.assert_called_once_with("task", system=None)
    smart.generate.assert_not_called()


def test_router_smart_tier_calls_smart_backend():
    cheap = _backend("cheap-out")
    smart = _backend("smart-out")
    r = Router(cheap=cheap, smart=smart)
    assert r.run("task", tier="smart", system="sys") == "smart-out"
    smart.generate.assert_called_once_with("task", system="sys")


def test_router_unknown_tier_raises():
    r = Router(cheap=_backend("x"), smart=_backend("y"))
    with pytest.raises(ValueError):
        r.run("task", tier="medium")


def test_router_retries_then_succeeds():
    smart = _backend(side_effect=[BackendError("fail1"), "ok"])
    r = Router(cheap=_backend("c"), smart=smart, retries=2, backoff_base=0)
    assert r.run("task", tier="smart") == "ok"
    assert smart.generate.call_count == 2


def test_router_raises_after_exhausting_retries():
    smart = _backend(side_effect=BackendError("always"))
    r = Router(cheap=_backend("c"), smart=smart, retries=2, backoff_base=0)
    with pytest.raises(BackendError):
        r.run("task", tier="smart")
    assert smart.generate.call_count == 3  # initial + 2 retries
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest digest/tests/test_router.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'digest.core.router'`.

- [ ] **Step 3: Implement `router.py`**

Create `digest/core/router.py`:
```python
from __future__ import annotations

import time

from digest.core.backends import Backend, BackendError

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
        assert last_error is not None
        raise last_error
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest digest/tests/test_router.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add digest/core/router.py digest/tests/test_router.py
git commit -m "feat: Model Router with tier dispatch + retry/backoff"
```

---

## Task 5: Wire-up factory + full suite

**Files:**
- Modify: `digest/core/router.py` (add `build_router` factory)
- Test: `digest/tests/test_router.py` (append)

- [ ] **Step 1: Write the failing test**

Append to `digest/tests/test_router.py`:
```python
def test_build_router_constructs_from_env_and_settings(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "gemma3:4b")
    monkeypatch.setenv("CLAUDE_BIN", "claude")

    from digest.core.router import build_router

    r = build_router()
    # cheap is Ollama, smart is Claude — verify by routing with mocks patched out
    from digest.core.backends import ClaudeBackend, OllamaBackend

    assert isinstance(r._backends["cheap"], OllamaBackend)
    assert isinstance(r._backends["smart"], ClaudeBackend)
    assert r._backends["cheap"].model == "gemma3:4b"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest digest/tests/test_router.py::test_build_router_constructs_from_env_and_settings -v`
Expected: FAIL — `ImportError: cannot import name 'build_router'`.

- [ ] **Step 3: Implement `build_router`**

Append to `digest/core/router.py` (add `import os` at top):
```python
def build_router() -> "Router":
    """Construct the default Router from environment variables.

    Reads OLLAMA_BASE_URL, OLLAMA_MODEL, CLAUDE_BIN. Call load_env() first
    if you need a .env file loaded into the environment.
    """
    from digest.core.backends import ClaudeBackend, OllamaBackend

    cheap = OllamaBackend(
        base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.environ.get("OLLAMA_MODEL", "gemma3:4b"),
    )
    smart = ClaudeBackend(claude_bin=os.environ.get("CLAUDE_BIN", "claude"))
    return Router(cheap=cheap, smart=smart)
```

- [ ] **Step 4: Run the full test suite**

Run: `uv run pytest -v`
Expected: PASS (all tests across config, backends, router — 15 passed: 4 config + 5 backends + 6 router).

- [ ] **Step 5: Commit**

```bash
git add digest/core/router.py digest/tests/test_router.py
git commit -m "feat: build_router factory from environment"
```

---

## Manual smoke test (optional, requires real services)

Not part of CI. Run only to confirm real wiring once Ollama is up and `claude` is authenticated:

```bash
uv run python -c "
from digest.core.config import load_env
from digest.core.router import build_router
load_env()
r = build_router()
print('CHEAP:', r.run('Say hi in 3 words.', tier='cheap'))
print('SMART:', r.run('Say hi in 3 words.', tier='smart'))
"
```
Expected: two short responses, one from Gemma, one from Claude.

---

## Done criteria for Milestone 1
- `uv run pytest` is green.
- `Router.run(task, tier)` dispatches cheap→Ollama, smart→Claude, retries the smart tier, and raises `BackendError`/`ValueError` appropriately.
- Config loads from `settings.yaml` (nested `.get()`) and `.env`.
- All work committed.

**Next:** Milestone 2 (Ingestion) — its plan will be written after this milestone is implemented and approved.
