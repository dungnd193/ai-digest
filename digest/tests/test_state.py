from digest.core.models import Article
from digest.core.state import SeenStore


def test_seenstore_empty_when_no_file(tmp_path):
    store = SeenStore(tmp_path / "seen.json")
    assert store.has("abc") is False


def test_seenstore_add_and_has(tmp_path):
    store = SeenStore(tmp_path / "seen.json")
    store.add("abc")
    assert store.has("abc") is True


def test_seenstore_persists_across_instances(tmp_path):
    path = tmp_path / "seen.json"
    s1 = SeenStore(path)
    s1.add("x")
    s1.save()
    s2 = SeenStore(path)
    assert s2.has("x") is True


def test_filter_new_returns_only_unseen(tmp_path):
    store = SeenStore(tmp_path / "seen.json")
    a = Article.create(url="https://a.com", title="A", source="F")
    b = Article.create(url="https://b.com", title="B", source="F")
    store.add(a.id)
    new = store.filter_new([a, b])
    assert new == [b]
