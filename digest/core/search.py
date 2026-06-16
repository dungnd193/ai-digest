from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

import requests


class SearchError(RuntimeError):
    """Raised when a search backend fails."""


@dataclass(frozen=True)
class SearchResult:
    url: str
    title: str = ""
    content: str = ""


class Searcher(Protocol):
    def search(self, query: str, *, max_results: int = 5) -> list[SearchResult]: ...


class TavilyBackend:
    """Search via the Tavily API. Wrapped behind Searcher so the backend is
    swappable (mirrors the Model Router seam)."""

    ENDPOINT = "https://api.tavily.com/search"

    def __init__(self, api_key: str, timeout: int = 30) -> None:
        self.api_key = api_key
        self.timeout = timeout

    def search(self, query: str, *, max_results: int = 5) -> list[SearchResult]:
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
        }
        try:
            resp = requests.post(self.ENDPOINT, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return [
                SearchResult(url=r["url"], title=r.get("title", ""), content=r.get("content", ""))
                for r in data.get("results", [])
            ]
        except Exception as exc:  # noqa: BLE001
            raise SearchError(f"Tavily search failed: {exc}") from exc


def build_searcher() -> Searcher:
    """Construct the default searcher from TAVILY_API_KEY."""
    return TavilyBackend(api_key=os.environ.get("TAVILY_API_KEY", ""))
