from unittest.mock import MagicMock

import pytest

from digest.agents.approval import ApprovalService, decode_callback, encode_callback
from digest.core.post_state import PostRecord, PostState, PostStore


def test_codec_roundtrip():
    assert decode_callback(encode_callback("pub", "2026-06-16:slug")) == ("pub", "2026-06-16:slug")


def test_decode_rejects_bad_action():
    with pytest.raises(ValueError):
        decode_callback("nope:key")


def _service(tmp_path):
    store = PostStore(tmp_path / "posts.json")
    f = tmp_path / "a.en.md"; f.write_text("---\ndraft: true\n---\n\nx\n")
    store.upsert(PostRecord(
        key="k", date="2026-06-16", slug="s", title="T", state=PostState.PENDING.value,
        files=[str(f)], article_ids=["id1"], message_id=1,
    ))
    publisher = MagicMock()
    seen = MagicMock()
    svc = ApprovalService(store=store, publisher=publisher, seen=seen, repo_dir=str(tmp_path))
    return svc, store, publisher, seen, f


def test_apply_publish(tmp_path):
    svc, store, publisher, seen, f = _service(tmp_path)
    svc.apply("pub", "k")
    publisher.mark_published.assert_called_once()
    publisher.commit_and_push.assert_called_once()
    seen.add_many.assert_called_once_with(["id1"])
    seen.save.assert_called_once()
    assert store.get("k").state == "published"


def test_apply_hold(tmp_path):
    svc, store, publisher, seen, f = _service(tmp_path)
    svc.apply("hold", "k")
    assert store.get("k").state == "held"
    publisher.commit_and_push.assert_not_called()


def test_apply_discard_deletes_files_and_marks_seen(tmp_path):
    svc, store, publisher, seen, f = _service(tmp_path)
    svc.apply("disc", "k")
    assert not f.exists()
    seen.add_many.assert_called_once_with(["id1"])
    assert store.get("k").state == "discarded"
