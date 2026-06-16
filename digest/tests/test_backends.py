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
