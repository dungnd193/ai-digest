from unittest.mock import MagicMock, patch

import pytest

from digest.core.telegram import TelegramClient, TelegramError


def _resp(ok=True, result=None):
    m = MagicMock()
    m.raise_for_status.return_value = None
    m.json.return_value = {"ok": ok, "result": result if result is not None else {}}
    return m


def test_send_message_returns_message_id():
    with patch("digest.core.telegram.requests.post",
               return_value=_resp(result={"message_id": 42})) as post:
        mid = TelegramClient("tok", "chat").send_message("hi")
    assert mid == 42
    url = post.call_args.args[0]
    assert url.endswith("/sendMessage")
    assert post.call_args.kwargs["json"]["chat_id"] == "chat"
    assert post.call_args.kwargs["json"]["text"] == "hi"


def test_send_message_with_buttons_builds_inline_keyboard():
    with patch("digest.core.telegram.requests.post",
               return_value=_resp(result={"message_id": 1})) as post:
        TelegramClient("tok", "chat").send_message(
            "pick", buttons=[("Yes", "pub:k"), ("No", "disc:k")]
        )
    markup = post.call_args.kwargs["json"]["reply_markup"]
    row = markup["inline_keyboard"][0]
    assert row[0] == {"text": "Yes", "callback_data": "pub:k"}
    assert row[1] == {"text": "No", "callback_data": "disc:k"}


def test_get_updates_returns_results():
    upd = [{"update_id": 5, "callback_query": {"id": "q", "data": "pub:k"}}]
    with patch("digest.core.telegram.requests.post", return_value=_resp(result=upd)):
        out = TelegramClient("tok", "chat").get_updates(offset=4)
    assert out == upd


def test_raises_telegramerror_on_http_failure():
    with patch("digest.core.telegram.requests.post", side_effect=Exception("boom")):
        with pytest.raises(TelegramError):
            TelegramClient("tok", "chat").send_message("hi")


def test_send_message_raises_telegramerror_when_message_id_missing():
    # ok=true but result has no message_id must surface as TelegramError, not KeyError
    with patch("digest.core.telegram.requests.post", return_value=_resp(result={})):
        with pytest.raises(TelegramError):
            TelegramClient("tok", "chat").send_message("hi")
