from unittest.mock import MagicMock

from digest.core.content_types import BlogPost, QualityVerdict
from digest.core.digest_types import Digest, DigestEntry
from digest.core.models import Article
from digest.pipeline import Pipeline


def _en_post(slug="s"):
    return BlogPost(lang="en", title="T", slug=slug, date="2026-06-16",
                    category="Tools", tags=("ai",), summary="sum", body="b",
                    sources=("https://a.com",))


def _build(**over):
    art = Article.create(url="https://a.com", title="A", source="F")
    deps = dict(
        ingestor=MagicMock(), processor=MagicMock(), clusterer=MagicMock(),
        analyst=MagicMock(), writer=MagicMock(), translator=MagicMock(),
        quality_gate=MagicMock(), publisher=MagicMock(), seen=MagicMock(),
        post_store=MagicMock(), reporter=MagicMock(), telegram=MagicMock(),
        languages=["en", "vi"], keywords=["k"], discovery_enabled=True,
        approval_required=True, repo_dir="/tmp/repo", date="2026-06-16",
        site_url="https://x",
    )
    deps.update(over)
    deps["ingestor"].gather.return_value = [art]
    deps["processor"].process_many.return_value = ["p"]
    deps["clusterer"].cluster.return_value = ["c"]
    deps["analyst"].analyze.return_value = Digest(entries=(DigestEntry(
        title="T", category="Tools", summary="sum", importance=4,
        sources=("https://a.com",), tags=("ai",)),))
    deps["writer"].write.return_value = [_en_post()]
    deps["translator"].translate.return_value = _en_post(slug="s")  # vi stand-in
    deps["quality_gate"].check.return_value = QualityVerdict(passed=True, reason="ok")
    deps["telegram"].send_message.return_value = 99
    # write_posts returns a path per post (mocked as strings)
    deps["publisher"].write_posts.return_value = ["/tmp/p.en.md", "/tmp/p.vi.md"]
    # reporter.daily_summary delegates to telegram (mirrors real Reporter behaviour)
    deps["reporter"].daily_summary.side_effect = lambda r: deps["telegram"].send_message("summary")
    return deps


def test_pipeline_approval_mode_writes_drafts_and_sends_buttons():
    deps = _build(approval_required=True)
    report = Pipeline(**deps).run()
    # drafts written
    assert deps["publisher"].write_posts.call_args.kwargs["draft"] is True
    # no auto commit in approval mode
    deps["publisher"].commit_and_push.assert_not_called()
    # telegram buttons sent, pending record stored
    assert deps["telegram"].send_message.called
    assert deps["post_store"].upsert.called
    # seen marked + saved
    deps["seen"].add_many.assert_called_once()
    deps["seen"].save.assert_called_once()
    assert report.posts_written >= 1


def test_pipeline_autopublish_mode_commits_and_pushes():
    deps = _build(approval_required=False)
    report = Pipeline(**deps).run()
    assert deps["publisher"].write_posts.call_args.kwargs["draft"] is False
    deps["publisher"].commit_and_push.assert_called_once()
    deps["telegram"].send_message.assert_called()  # daily summary still sent
    assert report.published >= 1


def test_pipeline_translates_when_vi_enabled():
    deps = _build(languages=["en", "vi"])
    Pipeline(**deps).run()
    deps["translator"].translate.assert_called()


def test_pipeline_skips_translation_when_only_en():
    deps = _build(languages=["en"])
    Pipeline(**deps).run()
    deps["translator"].translate.assert_not_called()


def test_pipeline_failed_quality_gate_skips_post():
    deps = _build(approval_required=False)
    deps["quality_gate"].check.return_value = QualityVerdict(passed=False, reason="bad")
    report = Pipeline(**deps).run()
    # nothing published, but seen still marked (articles were processed)
    assert report.published == 0
    deps["seen"].add_many.assert_called_once()
