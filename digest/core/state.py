from __future__ import annotations

import json
import logging
from pathlib import Path

from digest.core.models import Article

logger = logging.getLogger(__name__)


class SeenStore:
    """Tracks processed article ids for idempotency. JSON-backed.

    Call add()/add_many() then save() to persist. Marking-as-seen is the
    caller's decision (typically after successful publish), so loading and
    filtering never mutate state on disk.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._ids: set[str] = set()
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf-8") as fh:
                    self._ids = set(json.load(fh))
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("could not read seen store %s, starting empty: %s", self.path, exc)
                self._ids = set()

    def has(self, article_id: str) -> bool:
        return article_id in self._ids

    def add(self, article_id: str) -> None:
        self._ids.add(article_id)

    def add_many(self, ids: list[str]) -> None:
        self._ids.update(ids)

    def filter_new(self, articles: list[Article]) -> list[Article]:
        return [a for a in articles if a.id not in self._ids]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(sorted(self._ids), fh, indent=2)
