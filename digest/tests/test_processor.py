import json
from unittest.mock import MagicMock

from digest.agents.processor import Processor
from digest.core.models import Article

CATEGORIES = ["Research", "Tools", "Industry", "Tutorial", "Opinion"]


def _art(url="https://a.com"):
    return Article.create(url=url, title="T", source="S", content="body")


def test_processor_parses_model_json():
    router = MagicMock()
    router.run.return_value = json.dumps(
        {"summary": "s", "category": "Tools", "tags": ["ai", "llm"], "points": ["p1", "p2"]}
    )
    p = Processor(router, categories=CATEGORIES).process(_art())
    assert p.summary == "s"
    assert p.category == "Tools"
    assert p.tags == ("ai", "llm")
    assert p.points == ("p1", "p2")
    assert router.run.call_args.kwargs["tier"] == "cheap"


def test_processor_falls_back_on_offlist_category():
    router = MagicMock()
    router.run.return_value = json.dumps(
        {"summary": "s", "category": "Nonsense", "tags": [], "points": []}
    )
    p = Processor(router, categories=CATEGORIES).process(_art())
    assert p.category == "Industry"


def test_processor_falls_back_on_unparseable_output():
    router = MagicMock()
    router.run.return_value = "sorry, I cannot"
    p = Processor(router, categories=CATEGORIES).process(_art())
    assert p.category == "Industry"
    assert p.summary  # non-empty fallback (uses article content/title)


def test_process_many_skips_failures():
    router = MagicMock()
    router.run.side_effect = [
        json.dumps({"summary": "s", "category": "Tools", "tags": [], "points": []}),
        Exception("model down"),
    ]
    out = Processor(router, categories=CATEGORIES).process_many([_art("https://a.com"), _art("https://b.com")])
    assert len(out) == 1
