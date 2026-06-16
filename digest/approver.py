from __future__ import annotations

import logging
import os
import time
from pathlib import Path

from digest.agents.approval import ApprovalService, decode_callback
from digest.agents.publisher import Publisher
from digest.core.config import load_env
from digest.core.post_state import PostStore
from digest.core.state import SeenStore
from digest.core.telegram import TelegramClient, TelegramError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
_ROOT = Path(__file__).resolve().parent.parent


def _safe(call, *args) -> None:
    """Run a non-critical Telegram call; a stale callback (HTTP 400) or other
    transient error must NOT abort approval — the decision is already applied."""
    try:
        call(*args)
    except TelegramError as exc:
        logger.warning("non-fatal Telegram call failed: %s", exc)


def handle_update(update: dict, service: ApprovalService, telegram: TelegramClient) -> None:
    """Process one Telegram callback_query update."""
    cq = update.get("callback_query")
    if not cq:
        return
    try:
        action, key = decode_callback(cq.get("data", ""))
    except ValueError:
        _safe(telegram.answer_callback, cq["id"], "Unknown action")
        return
    message = service.apply(action, key)
    _safe(telegram.answer_callback, cq["id"], message)
    if cq.get("message"):
        _safe(telegram.edit_message_text, cq["message"]["message_id"], message)


def build_service() -> tuple[ApprovalService, TelegramClient]:
    load_env()
    telegram = TelegramClient(
        os.environ.get("TELEGRAM_BOT_TOKEN", ""), os.environ.get("TELEGRAM_CHAT_ID", "")
    )
    service = ApprovalService(
        store=PostStore(_ROOT / "digest" / "state" / "posts.json"),
        publisher=Publisher(site_dir=_ROOT / "site"),
        seen=SeenStore(_ROOT / "digest" / "state" / "seen.json"),
        repo_dir=str(_ROOT),
    )
    return service, telegram


def main() -> None:
    service, telegram = build_service()
    offset: int | None = None
    logger.info("approver started; long-polling for approvals")
    while True:
        try:
            updates = telegram.get_updates(offset=offset)
        except Exception as exc:  # noqa: BLE001
            logger.warning("getUpdates failed: %s", exc)
            time.sleep(5)
            continue
        if updates:
            service.store.reload()  # pick up posts from later orchestrator runs
        for upd in updates:
            offset = upd["update_id"] + 1
            try:
                handle_update(upd, service, telegram)
            except Exception as exc:  # noqa: BLE001 - one bad update must not kill the service
                logger.warning(
                    "handle_update failed for update %s: %s", upd.get("update_id"), exc
                )


if __name__ == "__main__":
    main()
