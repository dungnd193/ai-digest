from __future__ import annotations

import requests


class TelegramError(RuntimeError):
    """Raised when a Telegram Bot API call fails."""


class TelegramClient:
    """Thin wrapper over the Telegram Bot HTTP API (no external bot library)."""

    def __init__(self, token: str, chat_id: str, timeout: int = 30) -> None:
        self.base = f"https://api.telegram.org/bot{token}"
        self.chat_id = chat_id
        self.timeout = timeout

    def _call(self, method: str, payload: dict) -> dict:
        try:
            resp = requests.post(f"{self.base}/{method}", json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            raise TelegramError(f"{method} failed: {exc}") from exc
        if not data.get("ok", False):
            raise TelegramError(f"{method} returned not ok: {data}")
        return data.get("result", {})

    def send_message(self, text: str, *, buttons: list[tuple[str, str]] | None = None) -> int:
        payload: dict = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
        if buttons:
            payload["reply_markup"] = {
                "inline_keyboard": [
                    [{"text": label, "callback_data": data} for label, data in buttons]
                ]
            }
        return self._call("sendMessage", payload)["message_id"]

    def edit_message_text(self, message_id: int, text: str) -> None:
        self._call("editMessageText", {
            "chat_id": self.chat_id, "message_id": message_id,
            "text": text, "parse_mode": "HTML",
        })

    def answer_callback(self, callback_query_id: str, text: str = "") -> None:
        self._call("answerCallbackQuery", {"callback_query_id": callback_query_id, "text": text})

    def get_updates(self, offset: int | None = None, timeout: int = 25) -> list[dict]:
        payload: dict = {"timeout": timeout, "allowed_updates": ["callback_query"]}
        if offset is not None:
            payload["offset"] = offset
        return self._call("getUpdates", payload)
