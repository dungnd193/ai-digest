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
