from digest.core.models import Article, make_id


def test_make_id_is_stable_and_short():
    a = make_id("https://example.com/post")
    b = make_id("https://example.com/post")
    assert a == b
    assert len(a) == 16


def test_make_id_differs_by_url():
    assert make_id("https://a.com") != make_id("https://b.com")


def test_article_create_derives_id_from_url():
    art = Article.create(url="https://x.com/p", title="T", source="Feed")
    assert art.id == make_id("https://x.com/p")
    assert art.title == "T"
    assert art.source == "Feed"
    assert art.published == ""
    assert art.content == ""


def test_article_is_frozen_hashable():
    art = Article.create(url="https://x.com/p", title="T", source="F")
    {art}  # hashable -> no error
