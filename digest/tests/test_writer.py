from unittest.mock import MagicMock

from digest.agents.writer import Writer
from digest.core.digest_types import Digest, DigestEntry


def _entry(title="Multi-Agent Systems", sources=("https://a.com",)):
    return DigestEntry(
        title=title, category="Tools", summary="syn", importance=4,
        sources=sources, tags=("ai",),
    )


def test_writer_strips_leading_preamble():
    router = MagicMock()
    router.run.return_value = "Here's the article body:\n\n---\n\nReal content here."
    posts = Writer(router).write(Digest(entries=(_entry(),)), date="2026-06-16")
    body = posts[0].body
    assert not body.lower().startswith("here")
    assert "Real content here." in body


def test_writer_unwraps_code_fence():
    router = MagicMock()
    router.run.return_value = "```markdown\n# Heading\n\nBody.\n```"
    posts = Writer(router).write(Digest(entries=(_entry(),)), date="2026-06-16")
    before_sources = posts[0].body.split("## Sources")[0]
    assert "```" not in before_sources
    assert "Body." in before_sources


def test_writer_keeps_normal_body_starting_with_heres():
    # A legitimate sentence beginning with "Here's" (no trailing colon) is kept.
    router = MagicMock()
    router.run.return_value = "Here's why multi-agent systems matter. More text."
    posts = Writer(router).write(Digest(entries=(_entry(),)), date="2026-06-16")
    assert posts[0].body.startswith("Here's why")


def test_writer_produces_one_post_per_entry():
    router = MagicMock()
    router.run.return_value = "This is the article body."
    digest = Digest(entries=(_entry(), _entry(title="Second")))
    posts = Writer(router).write(digest, date="2026-06-16")
    assert len(posts) == 2
    assert router.run.call_args.kwargs["tier"] == "smart"


def test_writer_sets_fields_and_slug():
    router = MagicMock()
    router.run.return_value = "Body text."
    posts = Writer(router).write(Digest(entries=(_entry(),)), date="2026-06-16")
    p = posts[0]
    assert p.lang == "en"
    assert p.title == "Multi-Agent Systems"
    assert p.slug == "multi-agent-systems"
    assert p.date == "2026-06-16"
    assert p.category == "Tools"


def test_writer_appends_sources_section():
    router = MagicMock()
    router.run.return_value = "Body."
    posts = Writer(router).write(
        Digest(entries=(_entry(sources=("https://a.com", "https://b.com")),)),
        date="2026-06-16",
    )
    assert "## Sources" in posts[0].body
    assert "https://a.com" in posts[0].body
    assert "https://b.com" in posts[0].body


def test_writer_strips_hugo_shortcodes():
    router = MagicMock()
    router.run.return_value = 'Intro {{< figure src="x.png" >}} and {{% note %}}hi{{% /note %}} end.'
    posts = Writer(router).write(Digest(entries=(_entry(),)), date="2026-06-16")
    assert "{{<" not in posts[0].body
    assert "{{%" not in posts[0].body


def test_writer_strips_multiple_and_mixed_shortcodes():
    router = MagicMock()
    router.run.return_value = (
        "A {{< a >}} B {{% b %}} C {{% /b %}} D {{< c >}} E"
    )
    posts = Writer(router).write(Digest(entries=(_entry(),)), date="2026-06-16")
    assert "{{<" not in posts[0].body
    assert "{{%" not in posts[0].body
    assert ">}}" not in posts[0].body
    assert "%}}" not in posts[0].body


def test_writer_skips_entry_on_model_failure():
    router = MagicMock()
    router.run.side_effect = [Exception("down"), "Body."]
    posts = Writer(router).write(
        Digest(entries=(_entry(title="A"), _entry(title="B"))), date="2026-06-16"
    )
    assert [p.title for p in posts] == ["B"]
