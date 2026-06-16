import dataclasses
from unittest.mock import MagicMock

from digest.agents.translator import Translator
from digest.core.content_types import BlogPost


def _en_post(summary="A summary."):
    return BlogPost(
        lang="en", title="Multi-Agent Systems", slug="multi-agent-systems",
        date="2026-06-16", category="Tools", tags=("ai",),
        summary=summary, body="Body.\n\n## Sources\n- https://a.com",
        sources=("https://a.com",),
    )


def test_translator_gemma_only_single_cheap_call():
    router = MagicMock()
    router.run.return_value = "vi"
    post = dataclasses.replace(_en_post(), summary="")
    out = Translator(router, mode="gemma_only").translate(post)
    assert out.lang == "vi"
    # body (1) + title (1) = 2 cheap calls
    assert router.run.call_count == 2
    assert all(c.kwargs["tier"] == "cheap" for c in router.run.call_args_list)


def test_translator_claude_only_single_smart_call():
    router = MagicMock()
    router.run.return_value = "Nội dung."
    post = dataclasses.replace(_en_post(), summary="")
    Translator(router, mode="claude_only").translate(post)
    # body smart (1) + title smart (1) = 2
    assert router.run.call_count == 2
    assert all(c.kwargs["tier"] == "smart" for c in router.run.call_args_list)


def test_translator_draft_then_review_two_calls():
    router = MagicMock()
    router.run.side_effect = ["bản nháp", "bản hoàn chỉnh", "tiêu đề"]
    post = dataclasses.replace(_en_post(), summary="")
    out = Translator(router, mode="draft_then_review").translate(post)
    # body: cheap draft + smart review (2); title: cheap (1) = 3 calls
    assert router.run.call_count == 3
    assert out.body == "bản hoàn chỉnh"


def test_translator_preserves_metadata():
    router = MagicMock()
    router.run.return_value = "vi body"
    out = Translator(router, mode="gemma_only").translate(_en_post())
    assert out.category == "Tools"
    assert out.tags == ("ai",)
    assert out.sources == ("https://a.com",)
    assert out.date == "2026-06-16"


def test_translator_nonempty_summary_adds_one_call_per_mode():
    # Production path: a real (non-empty) summary is translated with one extra
    # single call, so counts are gemma=3, claude=3, draft_then_review=4.
    for mode, expected in (
        ("gemma_only", 3),
        ("claude_only", 3),
        ("draft_then_review", 4),
    ):
        router = MagicMock()
        router.run.return_value = "vi"
        out = Translator(router, mode=mode).translate(_en_post(summary="A summary."))
        assert router.run.call_count == expected, mode
        assert out.summary == "vi"
