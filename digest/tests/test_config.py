from pathlib import Path

import pytest

from digest.core.config import Settings, load_settings


def test_load_settings_reads_yaml(tmp_path):
    p = tmp_path / "settings.yaml"
    p.write_text("articles_per_run: 5\napproval_required: false\n")
    s = load_settings(p)
    assert s.articles_per_run == 5
    assert s.approval_required is False


def test_settings_exposes_nested_via_get(tmp_path):
    p = tmp_path / "settings.yaml"
    p.write_text("discovery:\n  enabled: true\n  keywords: [a, b]\n")
    s = load_settings(p)
    assert s.get("discovery.enabled") is True
    assert s.get("discovery.keywords") == ["a", "b"]


def test_settings_get_returns_default_for_missing(tmp_path):
    p = tmp_path / "settings.yaml"
    p.write_text("articles_per_run: 5\n")
    s = load_settings(p)
    assert s.get("nope.missing", "fallback") == "fallback"


def test_load_settings_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_settings(tmp_path / "absent.yaml")
