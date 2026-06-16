import json
from unittest.mock import MagicMock

from digest.agents.analyst import Analyst
from digest.core.digest_types import Cluster, ProcessedArticle
from digest.core.models import Article


def _p(title, url, cat="Tools"):
    art = Article.create(url=url, title=title, source="S")
    return ProcessedArticle(article=art, summary="s", category=cat, tags=("ai",), points=("p",))


def _cluster(title, url):
    return Cluster(topic=title, items=(_p(title, url),))


def test_analyst_builds_digest_from_model_json():
    clusters = [_cluster("Story A", "https://a.com")]
    router = MagicMock()
    router.run.return_value = json.dumps([
        {"title": "Story A", "category": "Tools", "summary": "synthesis",
         "importance": 5, "sources": ["https://a.com"], "tags": ["ai"]}
    ])
    digest = Analyst(router).analyze(clusters)
    assert len(digest.entries) == 1
    e = digest.entries[0]
    assert e.title == "Story A"
    assert e.importance == 5
    assert e.sources == ("https://a.com",)
    assert router.run.call_args.kwargs["tier"] == "smart"


def test_analyst_empty_clusters_returns_empty_digest():
    digest = Analyst(MagicMock()).analyze([])
    assert digest.entries == ()


def test_analyst_falls_back_on_unparseable_output():
    clusters = [_cluster("Story A", "https://a.com")]
    router = MagicMock()
    router.run.return_value = "cannot comply"
    digest = Analyst(router).analyze(clusters)
    assert len(digest.entries) == 1
    assert digest.entries[0].title == "Story A"
    assert digest.entries[0].sources == ("https://a.com",)
    assert 1 <= digest.entries[0].importance <= 5
