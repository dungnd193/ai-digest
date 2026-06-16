import json
from unittest.mock import MagicMock

from digest.agents.clusterer import Clusterer
from digest.core.digest_types import ProcessedArticle
from digest.core.models import Article


def _p(title):
    art = Article.create(url=f"https://{title}.com", title=title, source="S")
    return ProcessedArticle(article=art, summary="s", category="Tools", tags=(), points=())


def test_clusterer_groups_by_model_indices():
    items = [_p("a"), _p("b"), _p("c")]
    router = MagicMock()
    router.run.return_value = json.dumps([[0, 2], [1]])
    clusters = Clusterer(router).cluster(items)
    assert len(clusters) == 2
    assert {i.article.title for i in clusters[0].items} == {"a", "c"}
    assert clusters[0].topic == "a"
    assert router.run.call_args.kwargs["tier"] == "cheap"


def test_clusterer_empty_input_returns_empty():
    assert Clusterer(MagicMock()).cluster([]) == []


def test_clusterer_falls_back_to_singletons_on_bad_output():
    items = [_p("a"), _p("b")]
    router = MagicMock()
    router.run.return_value = "not json"
    clusters = Clusterer(router).cluster(items)
    assert len(clusters) == 2
    assert all(len(c.items) == 1 for c in clusters)


def test_clusterer_ignores_out_of_range_indices():
    items = [_p("a"), _p("b")]
    router = MagicMock()
    router.run.return_value = json.dumps([[0, 99], [1]])
    clusters = Clusterer(router).cluster(items)
    # index 99 dropped; group becomes {a}, plus {b}
    titles = [{i.article.title for i in c.items} for c in clusters]
    assert {"a"} in titles and {"b"} in titles
