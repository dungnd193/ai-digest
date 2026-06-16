from digest.core.post_state import PostRecord, PostState, PostStore


def _rec(key="2026-06-16:ai-agents"):
    return PostRecord(
        key=key, date="2026-06-16", slug="ai-agents", title="T",
        state=PostState.PENDING.value, files=["a.en.md"], article_ids=["id1"],
        message_id=None,
    )


def test_store_upsert_and_get(tmp_path):
    store = PostStore(tmp_path / "posts.json")
    store.upsert(_rec())
    got = store.get("2026-06-16:ai-agents")
    assert got.title == "T"
    assert got.state == "pending_approval"


def test_store_persists(tmp_path):
    path = tmp_path / "posts.json"
    PostStore(path).upsert(_rec()); PostStore(path)  # reload
    store2 = PostStore(path)
    store2.upsert(_rec())  # idempotent reload works
    assert store2.get("2026-06-16:ai-agents") is not None


def test_store_set_state_and_pending(tmp_path):
    store = PostStore(tmp_path / "posts.json")
    store.upsert(_rec())
    store.set_state("2026-06-16:ai-agents", PostState.PUBLISHED)
    assert store.get("2026-06-16:ai-agents").state == "published"
    assert store.pending() == []  # no longer pending


def test_store_pending_lists_only_pending(tmp_path):
    store = PostStore(tmp_path / "posts.json")
    store.upsert(_rec("k1"))
    r2 = _rec("k2"); store.upsert(r2)
    store.set_state("k2", PostState.PUBLISHED)
    assert [r.key for r in store.pending()] == ["k1"]
