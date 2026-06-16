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
