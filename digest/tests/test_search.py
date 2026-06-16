from unittest.mock import MagicMock, patch

import pytest

from digest.core.search import SearchError, SearchResult, TavilyBackend, build_searcher


def test_tavily_search_returns_results():
    fake = MagicMock()
    fake.raise_for_status.return_value = None
    fake.json.return_value = {
        "results": [
            {"url": "https://a.com", "title": "A", "content": "ca"},
            {"url": "https://b.com", "title": "B", "content": "cb"},
        ]
    }
    with patch("digest.core.search.requests.post", return_value=fake) as post:
        be = TavilyBackend(api_key="k")
        out = be.search("ai agents", max_results=2)

    assert out == [
        SearchResult(url="https://a.com", title="A", content="ca"),
        SearchResult(url="https://b.com", title="B", content="cb"),
    ]
    payload = post.call_args.kwargs["json"]
    assert payload["query"] == "ai agents"
    assert payload["max_results"] == 2
    assert payload["api_key"] == "k"


def test_tavily_search_raises_searcherror_on_http_failure():
    with patch("digest.core.search.requests.post", side_effect=Exception("boom")):
        be = TavilyBackend(api_key="k")
        with pytest.raises(SearchError):
            be.search("x")


def test_tavily_search_tolerates_missing_fields():
    fake = MagicMock()
    fake.raise_for_status.return_value = None
    fake.json.return_value = {"results": [{"url": "https://a.com"}]}
    with patch("digest.core.search.requests.post", return_value=fake):
        be = TavilyBackend(api_key="k")
        out = be.search("x")
    assert out == [SearchResult(url="https://a.com", title="", content="")]


def test_tavily_missing_url_raises_searcherror():
    fake = MagicMock()
    fake.raise_for_status.return_value = None
    fake.json.return_value = {"results": [{"title": "no url"}]}
    with patch("digest.core.search.requests.post", return_value=fake):
        with pytest.raises(SearchError):
            TavilyBackend(api_key="k").search("x")


def test_build_searcher_uses_env_key(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "abc")
    from digest.core.search import TavilyBackend, build_searcher
    s = build_searcher()
    assert isinstance(s, TavilyBackend)
    assert s.api_key == "abc"
