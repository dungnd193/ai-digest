from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass
class Settings:
    """Behavior config loaded from settings.yaml. Attribute access for top-level
    keys; dotted .get() for nested values."""

    _data: dict[str, Any] = field(default_factory=dict)

    def __getattr__(self, name: str) -> Any:
        if name == "_data":
            raise AttributeError(name)
        try:
            return self._data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def get(self, dotted_key: str, default: Any = None) -> Any:
        node: Any = self._data
        for part in dotted_key.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node


def load_settings(path: str | Path) -> Settings:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"settings file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return Settings(_data=data)


def load_env(path: str | Path | None = None) -> None:
    """Load secrets/paths from a .env file into os.environ (no-op if absent)."""
    if path is None:
        load_dotenv()
    else:
        load_dotenv(dotenv_path=Path(path))
