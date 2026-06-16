from __future__ import annotations

import logging
from pathlib import Path

from digest.agents.publisher import Publisher
from digest.core.post_state import PostState, PostStore
from digest.core.state import SeenStore

logger = logging.getLogger(__name__)

_ACTIONS = {"pub", "hold", "disc"}


def encode_callback(action: str, key: str) -> str:
    if action not in _ACTIONS:
        raise ValueError(f"bad action: {action}")
    return f"{action}:{key}"


def decode_callback(data: str) -> tuple[str, str]:
    action, _, key = data.partition(":")
    if action not in _ACTIONS or not key:
        raise ValueError(f"bad callback data: {data!r}")
    return action, key


class ApprovalService:
    """Applies an approval decision to files, post state, and the seen store."""

    def __init__(
        self,
        *,
        store: PostStore,
        publisher: Publisher,
        seen: SeenStore,
        repo_dir: str,
    ) -> None:
        self.store = store
        self.publisher = publisher
        self.seen = seen
        self.repo_dir = repo_dir

    def apply(self, action: str, key: str) -> str:
        rec = self.store.get(key)
        if rec is None:
            return f"Unknown post: {key}"

        if action == "pub":
            self.publisher.mark_published(rec.files)
            self.publisher.commit_and_push(f"post: {rec.title}", repo_dir=self.repo_dir)
            self._mark_seen(rec.article_ids)
            self.store.set_state(key, PostState.PUBLISHED)
            return f"✅ Published: {rec.title}"

        if action == "hold":
            self.store.set_state(key, PostState.HELD)
            return f"✏️ Held: {rec.title}"

        if action == "disc":
            repo = Path(self.repo_dir).resolve()
            for f in rec.files:
                target = Path(f).resolve()
                if not target.is_relative_to(repo):
                    logger.warning("refusing to delete %s: outside repo %s", target, repo)
                    continue
                try:
                    target.unlink(missing_ok=True)
                except OSError as exc:
                    logger.warning("could not delete %s: %s", f, exc)
            self._mark_seen(rec.article_ids)
            self.store.set_state(key, PostState.DISCARDED)
            return f"❌ Discarded: {rec.title}"

        return f"Unknown action: {action}"

    def _mark_seen(self, ids: list[str]) -> None:
        self.seen.add_many(ids)
        self.seen.save()
