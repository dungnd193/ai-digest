from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path


class PostState(str, Enum):
    DRAFT = "draft"
    PENDING = "pending_approval"
    PUBLISHED = "published"
    HELD = "held"
    DISCARDED = "discarded"


@dataclass
class PostRecord:
    key: str
    date: str
    slug: str
    title: str
    state: str
    files: list[str] = field(default_factory=list)
    article_ids: list[str] = field(default_factory=list)
    message_id: int | None = None


class PostStore:
    """Persists post lifecycle records to JSON, keyed by `key` (date:slug)."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._records: dict[str, PostRecord] = {}
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as fh:
                for k, v in json.load(fh).items():
                    self._records[k] = PostRecord(**v)

    def get(self, key: str) -> PostRecord | None:
        return self._records.get(key)

    def upsert(self, record: PostRecord) -> None:
        self._records[record.key] = record
        self.save()

    def set_state(self, key: str, state: PostState) -> None:
        rec = self._records[key]
        rec.state = state.value
        self.save()

    def pending(self) -> list[PostRecord]:
        return [r for r in self._records.values() if r.state == PostState.PENDING.value]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump({k: asdict(v) for k, v in self._records.items()}, fh, indent=2)
