from pathlib import Path
from unittest.mock import MagicMock, patch

from digest.agents.publisher import Publisher
from digest.core.content_types import BlogPost


def _post(lang="en", slug="ai-agents"):
    return BlogPost(
        lang=lang, title="T", slug=slug, date="2026-06-16", category="Tools",
        tags=("ai",), summary="s", body="Body.", sources=("https://a.com",),
    )


def test_write_posts_creates_files(tmp_path):
    pub = Publisher(site_dir=tmp_path)
    paths = pub.write_posts([_post("en"), _post("vi")])
    assert len(paths) == 2
    posts_dir = tmp_path / "content" / "posts"
    assert (posts_dir / "2026-06-16-ai-agents.en.md").exists()
    assert (posts_dir / "2026-06-16-ai-agents.vi.md").exists()


def test_write_posts_content_has_front_matter(tmp_path):
    pub = Publisher(site_dir=tmp_path)
    [path] = pub.write_posts([_post("en")])
    text = Path(path).read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "title:" in text
    assert "Body." in text


def test_write_posts_draft_sets_flag(tmp_path):
    pub = Publisher(site_dir=tmp_path)
    [path] = pub.write_posts([_post("en")], draft=True)
    assert "draft: true" in Path(path).read_text(encoding="utf-8")


def _completed(returncode=0, stdout="", stderr=""):
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    m.stderr = stderr
    return m


def test_commit_and_push_happy_path(tmp_path):
    pub = Publisher(site_dir=tmp_path)
    with patch("digest.agents.publisher.subprocess.run", return_value=_completed(0)) as run:
        ok = pub.commit_and_push("msg", repo_dir=tmp_path)
    assert ok is True
    cmds = [c.args[0][:2] for c in run.call_args_list]
    assert ["git", "add"] in cmds
    assert ["git", "commit"] in cmds
    assert ["git", "push"] in cmds


def test_commit_and_push_nothing_to_commit_returns_false(tmp_path):
    pub = Publisher(site_dir=tmp_path)

    def fake_run(cmd, **kw):
        if cmd[:2] == ["git", "commit"]:
            return _completed(1, stdout="nothing to commit, working tree clean")
        return _completed(0)

    with patch("digest.agents.publisher.subprocess.run", side_effect=fake_run):
        ok = pub.commit_and_push("msg", repo_dir=tmp_path)
    assert ok is False


def test_commit_and_push_push_failure_retries_then_false(tmp_path):
    pub = Publisher(site_dir=tmp_path)

    def fake_run(cmd, **kw):
        if cmd[:2] == ["git", "push"]:
            return _completed(1, stderr="network error")
        return _completed(0)

    with patch("digest.agents.publisher.subprocess.run", side_effect=fake_run) as run:
        ok = pub.commit_and_push("msg", repo_dir=tmp_path, retries=2)
    assert ok is False
    push_calls = [c for c in run.call_args_list if c.args[0][:2] == ["git", "push"]]
    assert len(push_calls) == 3  # initial + 2 retries


def test_commit_and_push_skip_push(tmp_path):
    pub = Publisher(site_dir=tmp_path)
    with patch("digest.agents.publisher.subprocess.run", return_value=_completed(0)) as run:
        ok = pub.commit_and_push("msg", repo_dir=tmp_path, push=False)
    assert ok is True
    assert not any(c.args[0][:2] == ["git", "push"] for c in run.call_args_list)
