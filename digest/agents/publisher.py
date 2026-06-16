from __future__ import annotations

import logging
import subprocess
import time
from pathlib import Path

from digest.core.content_types import BlogPost
from digest.core.render import post_filename, render_post

logger = logging.getLogger(__name__)


class Publisher:
    """Writes blog posts into a Hugo site dir and commits/pushes them.
    File-writing and git are separate methods so each is independently testable."""

    def __init__(self, site_dir: str | Path, posts_subdir: str = "content/posts") -> None:
        self.site_dir = Path(site_dir)
        self.posts_dir = self.site_dir / posts_subdir

    def write_posts(self, posts: list[BlogPost], *, draft: bool = False) -> list[Path]:
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for post in posts:
            path = self.posts_dir / post_filename(post)
            path.write_text(render_post(post, draft=draft), encoding="utf-8")
            written.append(path)
        return written

    def commit_and_push(
        self,
        message: str,
        *,
        repo_dir: str | Path | None = None,
        remote: str = "origin",
        push: bool = True,
        retries: int = 2,
    ) -> bool:
        cwd = str(repo_dir or self.site_dir)

        self._git(["git", "add", "-A"], cwd)
        commit = self._git(["git", "commit", "-m", message], cwd)
        if commit.returncode != 0:
            if "nothing to commit" in (commit.stdout + commit.stderr).lower():
                logger.info("nothing to commit")
                return False
            logger.warning("git commit failed: %s", commit.stderr.strip())
            return False

        if not push:
            return True

        for attempt in range(retries + 1):
            pushed = self._git(["git", "push", remote], cwd)
            if pushed.returncode == 0:
                return True
            logger.warning("git push attempt %d failed: %s", attempt + 1, pushed.stderr.strip())
            if attempt < retries:
                time.sleep(2**attempt)
        logger.error("git push exhausted retries; commit kept locally")
        return False

    def mark_published(self, paths: list) -> None:
        """Flip draft front-matter to published for already-written files."""
        from pathlib import Path as _Path
        for p in paths:
            path = _Path(p)
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace("draft: true", "draft: false", 1), encoding="utf-8")

    @staticmethod
    def _git(cmd: list[str], cwd: str):
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
