from types import SimpleNamespace
from unittest.mock import patch

from digest.agents.collector import Collector
from digest.core.models import make_id


def _feed(title, entries):
    return SimpleNamespace(feed=SimpleNamespace(title=title), entries=entries, bozo=0)


def _entry(link, title, summary="", published=""):
    return {"link": link, "title": title, "summary": summary, "published": published}


def test_collector_parses_entries_into_articles():
    parsed = _feed("My Feed", [_entry("https://a.com/1", "First", "body", "2026-06-16")])
    with patch("digest.agents.collector.feedparser.parse", return_value=parsed):
        arts = Collector(["http://feed"]).collect()
    assert len(arts) == 1
    assert arts[0].id == make_id("https://a.com/1")
    assert arts[0].title == "First"
    assert arts[0].source == "My Feed"
    assert arts[0].content == "body"
    assert arts[0].published == "2026-06-16"


def test_collector_skips_broken_feed_and_continues():
    good = _feed("Good", [_entry("https://a.com/1", "ok")])

    def fake_parse(url):
        if url == "bad":
            raise Exception("network down")
        return good

    with patch("digest.agents.collector.feedparser.parse", side_effect=fake_parse):
        arts = Collector(["bad", "good"]).collect()
    assert len(arts) == 1
    assert arts[0].title == "ok"


def test_collector_skips_bozo_feed_and_continues():
    from types import SimpleNamespace
    bad = SimpleNamespace(feed=SimpleNamespace(title="bad"), entries=[], bozo=1, bozo_exception="boom")
    good = _feed("Good", [_entry("https://a.com/1", "ok")])
    def fake_parse(url):
        return bad if url == "bad" else good
    with patch("digest.agents.collector.feedparser.parse", side_effect=fake_parse):
        arts = Collector(["bad", "good"]).collect()
    assert [a.title for a in arts] == ["ok"]


def test_collector_skips_entries_without_link():
    parsed = _feed("F", [{"title": "no link"}, _entry("https://a.com/1", "has link")])
    with patch("digest.agents.collector.feedparser.parse", return_value=parsed):
        arts = Collector(["http://feed"]).collect()
    assert [a.title for a in arts] == ["has link"]
