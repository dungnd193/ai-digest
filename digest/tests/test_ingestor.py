from unittest.mock import MagicMock

from digest.agents.ingestor import Ingestor
from digest.core.models import Article


def _art(url, title="T"):
    return Article.create(url=url, title=title, source="S")


def test_ingestor_combines_collector_and_discovery():
    collector = MagicMock()
    collector.collect.return_value = [_art("https://a.com")]
    discovery = MagicMock()
    discovery.discover.return_value = [_art("https://b.com")]
    seen = MagicMock()
    seen.filter_new.side_effect = lambda arts: arts

    out = Ingestor(collector, discovery, seen).gather(keywords=["k"])
    assert {a.url for a in out} == {"https://a.com", "https://b.com"}


def test_ingestor_dedupes_same_url_from_both_sources():
    collector = MagicMock()
    collector.collect.return_value = [_art("https://dup.com")]
    discovery = MagicMock()
    discovery.discover.return_value = [_art("https://dup.com")]
    seen = MagicMock()
    seen.filter_new.side_effect = lambda arts: arts

    out = Ingestor(collector, discovery, seen).gather(keywords=["k"])
    assert len(out) == 1


def test_ingestor_filters_already_seen():
    a, b = _art("https://a.com"), _art("https://b.com")
    collector = MagicMock()
    collector.collect.return_value = [a, b]
    discovery = MagicMock()
    discovery.discover.return_value = []
    seen = MagicMock()
    seen.filter_new.return_value = [b]  # a already seen

    out = Ingestor(collector, discovery, seen).gather(keywords=["k"])
    assert out == [b]


def test_ingestor_skips_discovery_when_disabled():
    collector = MagicMock()
    collector.collect.return_value = [_art("https://a.com")]
    discovery = MagicMock()
    seen = MagicMock()
    seen.filter_new.side_effect = lambda arts: arts

    out = Ingestor(collector, discovery, seen).gather(keywords=["k"], discovery_enabled=False)
    assert len(out) == 1
    discovery.discover.assert_not_called()
