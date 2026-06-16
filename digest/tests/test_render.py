import yaml

from digest.core.content_types import BlogPost
from digest.core.render import post_filename, render_post


def _post(lang="en"):
    return BlogPost(
        lang=lang, title='AI: "Agents" & more', slug="ai-agents",
        date="2026-06-16", category="Tools", tags=("ai", "llm"),
        summary="A summary.", body="# Heading\n\nBody text.",
        sources=("https://a.com",),
    )


def _split_front_matter(text):
    assert text.startswith("---\n")
    _, fm, body = text.split("---\n", 2)
    return yaml.safe_load(fm), body


def test_render_post_front_matter_fields():
    fm, body = _split_front_matter(render_post(_post()))
    assert fm["title"] == 'AI: "Agents" & more'
    assert fm["date"] == "2026-06-16"
    assert fm["lang"] == "en"
    assert fm["slug"] == "ai-agents"
    assert fm["categories"] == ["Tools"]
    assert fm["tags"] == ["ai", "llm"]
    assert fm["draft"] is False
    assert "Body text." in body


def test_render_post_draft_flag():
    fm, _ = _split_front_matter(render_post(_post(), draft=True))
    assert fm["draft"] is True


def test_post_filename_uses_date_slug_lang():
    assert post_filename(_post("en")) == "2026-06-16-ai-agents.en.md"
    assert post_filename(_post("vi")) == "2026-06-16-ai-agents.vi.md"
