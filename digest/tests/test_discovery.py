from unittest.mock import MagicMock

from digest.agents.discovery import Discovery
from digest.core.search import SearchError, SearchResult


def _searcher(mapping):
    s = MagicMock()
    s.search.side_effect = lambda q, max_results=5: mapping[q]
    return s


def test_discovery_converts_results_to_articles():
    s = _searcher({"ai": [SearchResult(url="https://a.com", title="A", content="c")]})
    arts = Discovery(searcher=s).discover(["ai"])
    assert len(arts) == 1
    assert arts[0].url == "https://a.com"
    assert arts[0].source == "discovery:ai"
    assert arts[0].content == "c"


def test_discovery_dedupes_across_keywords():
    r = SearchResult(url="https://dup.com", title="D", content="c")
    s = _searcher({"k1": [r], "k2": [r]})
    arts = Discovery(searcher=s).discover(["k1", "k2"])
    assert len(arts) == 1


def test_discovery_skips_keyword_on_search_error():
    s = MagicMock()
    s.search.side_effect = SearchError("boom")
    arts = Discovery(searcher=s).discover(["k1"])
    assert arts == []


def test_discovery_relevance_filter_drops_no_answers():
    s = _searcher({"ai": [
        SearchResult(url="https://yes.com", title="Y", content="relevant"),
        SearchResult(url="https://no.com", title="N", content="spam"),
    ]})
    router = MagicMock()
    # cheap model says yes for the first, no for the second
    router.run.side_effect = ["YES", "no, unrelated"]
    arts = Discovery(searcher=s, router=router).discover(["ai"])
    assert [a.url for a in arts] == ["https://yes.com"]
    assert router.run.call_count == 2
    assert router.run.call_args_list[0].kwargs["tier"] == "cheap"
