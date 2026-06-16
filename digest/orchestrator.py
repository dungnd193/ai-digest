from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

import yaml

from digest.agents.analyst import Analyst
from digest.agents.clusterer import Clusterer
from digest.agents.collector import Collector
from digest.agents.discovery import Discovery
from digest.agents.ingestor import Ingestor
from digest.agents.processor import Processor
from digest.agents.quality_gate import QualityGate
from digest.agents.reporter import Reporter
from digest.agents.translator import Translator
from digest.agents.writer import Writer
from digest.agents.publisher import Publisher
from digest.core.config import load_env, load_settings
from digest.core.post_state import PostStore
from digest.core.router import build_router
from digest.core.search import build_searcher
from digest.core.state import SeenStore
from digest.core.telegram import TelegramClient
from digest.pipeline import Pipeline

_ROOT = Path(__file__).resolve().parent.parent


def _setup_logging(run_ts: str) -> Path:
    """Log to console AND a per-run file with timestamps, so each step/agent's
    timing is captured for performance review (digest/state/runs/<ts>.log)."""
    runs_dir = _ROOT / "digest" / "state" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    log_path = runs_dir / f"{run_ts.replace(':', '-')}.log"
    fmt = logging.Formatter("%(asctime)s %(levelname)-5s %(name)s | %(message)s", "%H:%M:%S")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    fh = logging.FileHandler(log_path, encoding="utf-8"); fh.setFormatter(fmt)
    sh = logging.StreamHandler(); sh.setFormatter(fmt)
    root.handlers = [fh, sh]
    return log_path


def main(run_date: str | None = None) -> None:
    load_env()
    run_ts = run_date or datetime.now().isoformat(timespec="seconds")
    log_path = _setup_logging(run_ts)
    logging.getLogger(__name__).info("AI Digest run %s — logging to %s", run_ts, log_path)

    settings = load_settings(_ROOT / "digest" / "config" / "settings.yaml")
    feeds_cfg = yaml.safe_load((_ROOT / "digest" / "config" / "feeds.yaml").read_text())

    router = build_router(settings.get("model_mode", "both"))
    searcher = build_searcher()
    seen = SeenStore(_ROOT / "digest" / "state" / "seen.json")
    telegram = TelegramClient(
        os.environ.get("TELEGRAM_BOT_TOKEN", ""), os.environ.get("TELEGRAM_CHAT_ID", "")
    )
    pipeline = Pipeline(
        ingestor=Ingestor(Collector(feeds_cfg.get("feeds", [])),
                          Discovery(searcher, router), seen),
        processor=Processor(router, settings.get("categories", [])),
        clusterer=Clusterer(router),
        analyst=Analyst(router),
        writer=Writer(router),
        translator=Translator(router, settings.get("translator_mode", "draft_then_review")),
        quality_gate=QualityGate(router),
        publisher=Publisher(site_dir=_ROOT / "site"),
        seen=seen,
        post_store=PostStore(_ROOT / "digest" / "state" / "posts.json"),
        reporter=Reporter(telegram),
        telegram=telegram,
        languages=settings.get("languages", ["en"]),
        keywords=settings.get("discovery.keywords", []),
        discovery_enabled=settings.get("discovery.enabled", True),
        approval_required=settings.get("approval_required", True),
        repo_dir=str(_ROOT),
        date=run_ts,
        site_url=os.environ.get("SITE_URL", ""),
        max_articles=settings.get("articles_per_run", 0),
        publish_enabled=settings.get("steps.publish", True),
        model_mode=settings.get("model_mode", "both"),
    )
    pipeline.run()


if __name__ == "__main__":
    main()
