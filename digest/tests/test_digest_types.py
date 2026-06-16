from digest.core.digest_types import Cluster, Digest, DigestEntry, ProcessedArticle
from digest.core.models import Article


def _art(url="https://a.com"):
    return Article.create(url=url, title="T", source="S")


def test_processed_article_holds_enrichment():
    p = ProcessedArticle(
        article=_art(), summary="s", category="Tools", tags=("ai",), points=("p1",)
    )
    assert p.article.url == "https://a.com"
    assert p.category == "Tools"
    assert p.tags == ("ai",)


def test_cluster_groups_processed():
    p = ProcessedArticle(article=_art(), summary="s", category="Tools", tags=(), points=())
    c = Cluster(topic="A topic", items=(p,))
    assert c.items[0] is p


def test_digest_holds_entries():
    e = DigestEntry(
        title="T", category="Tools", summary="syn", importance=4,
        sources=("https://a.com",), tags=("ai",),
    )
    d = Digest(entries=(e,))
    assert d.entries[0].importance == 4
