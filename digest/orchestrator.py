from __future__ import annotations

import logging
import os
from datetime import date as _date
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

logging.basicConfig(level=logging.INFO)
_ROOT = Path(__file__).resolve().parent.parent


def main(run_date: str | None = None) -> None:
    load_env()
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
        date=run_date or _date.today().isoformat(),
        site_url=os.environ.get("SITE_URL", ""),
        max_articles=settings.get("articles_per_run", 0),
        publish_enabled=settings.get("steps.publish", True),
    )
    pipeline.run()


if __name__ == "__main__":
    main()
