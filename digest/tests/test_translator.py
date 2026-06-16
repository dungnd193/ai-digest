from unittest.mock import MagicMock

from digest.agents.translator import Translator
from digest.core.content_types import BlogPost


def _en_post():
    return BlogPost(
        lang="en", title="Multi-Agent Systems", slug="multi-agent-systems",
        date="2026-06-16", category="Tools", tags=("ai",),
        summary="A summary.", body="Body.\n\n## Sources\n- https://a.com",
        sources=("https://a.com",),
    )


def test_translator_gemma_only_single_cheap_call():
    router = MagicMock()
    router.run.return_value = "vi"
    post = _en_post()
    object.__setattr__(post, "summary", "")  # frozen dataclass; clear summary
    out = Translator(router, mode="gemma_only").translate(post)
    assert out.lang == "vi"
    # body (1) + title (1) = 2 cheap calls
    assert router.run.call_count == 2
    assert all(c.kwargs["tier"] == "cheap" for c in router.run.call_args_list)


def test_translator_claude_only_single_smart_call():
    router = MagicMock()
    router.run.return_value = "Nội dung."
    post = _en_post()
    object.__setattr__(post, "summary", "")
    Translator(router, mode="claude_only").translate(post)
    # body smart (1) + title smart (1) = 2
    assert router.run.call_count == 2
    assert all(c.kwargs["tier"] == "smart" for c in router.run.call_args_list)


def test_translator_draft_then_review_two_calls():
    router = MagicMock()
    router.run.side_effect = ["bản nháp", "bản hoàn chỉnh", "tiêu đề"]
    post = _en_post()
    object.__setattr__(post, "summary", "")
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
