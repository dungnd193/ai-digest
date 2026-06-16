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


def test_router_rejects_negative_retries():
    import pytest
    from digest.core.backends import BackendError  # noqa
    with pytest.raises(ValueError):
        Router(cheap=_backend("c"), smart=_backend("s"), retries=-1)


def test_router_retries_zero_single_attempt_then_raises():
    from digest.core.backends import BackendError
    smart = _backend(side_effect=BackendError("x"))
    r = Router(cheap=_backend("c"), smart=smart, retries=0, backoff_base=0)
    import pytest
    with pytest.raises(BackendError):
        r.run("t", tier="smart")
    assert smart.generate.call_count == 1


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
