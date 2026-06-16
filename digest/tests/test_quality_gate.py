import json
from unittest.mock import MagicMock

from digest.agents.quality_gate import QualityGate
from digest.core.content_types import BlogPost


def _post():
    return BlogPost(
        lang="en", title="T", slug="t", date="2026-06-16", category="Tools",
        tags=(), summary="s", body="Body.\n\n## Sources\n- https://a.com",
        sources=("https://a.com",),
    )


def test_quality_gate_pass():
    router = MagicMock()
    router.run.return_value = json.dumps({"pass": True, "reason": "grounded"})
    v = QualityGate(router).check(_post())
    assert v.passed is True
    assert router.run.call_args.kwargs["tier"] == "smart"


def test_quality_gate_fail():
    router = MagicMock()
    router.run.return_value = json.dumps({"pass": False, "reason": "unsupported claim"})
    v = QualityGate(router).check(_post())
    assert v.passed is False
    assert "unsupported" in v.reason


def test_quality_gate_fails_open_on_unparseable():
    router = MagicMock()
    router.run.return_value = "I think it's fine maybe"
    v = QualityGate(router).check(_post())
    assert v.passed is True
    assert "inconclusive" in v.reason.lower()


def test_quality_gate_fails_open_on_model_error():
    router = MagicMock()
    router.run.side_effect = Exception("model down")
    v = QualityGate(router).check(_post())
    assert v.passed is True
