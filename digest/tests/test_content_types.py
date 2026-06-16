from digest.core.content_types import BlogPost, QualityVerdict, slugify


def test_slugify_basic():
    assert slugify("Hello, World!") == "hello-world"


def test_slugify_collapses_and_trims():
    assert slugify("  Multi   Agent  AI  ") == "multi-agent-ai"


def test_slugify_strips_non_ascii_punctuation():
    assert slugify("GPT-5: what's new?") == "gpt-5-what-s-new"


def test_blogpost_holds_fields():
    p = BlogPost(
        lang="en", title="T", slug="t", date="2026-06-16", category="Tools",
        tags=("ai",), summary="s", body="# body", sources=("https://a.com",),
    )
    assert p.lang == "en"
    assert p.sources == ("https://a.com",)


def test_quality_verdict():
    v = QualityVerdict(passed=False, reason="unsupported claim")
    assert v.passed is False
    assert "unsupported" in v.reason
