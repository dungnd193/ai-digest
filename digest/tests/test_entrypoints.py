import importlib
from unittest.mock import MagicMock

from digest.approver import handle_update
from digest.core.telegram import TelegramError


def test_entrypoints_import_without_side_effects():
    # importing must not call network/models
    importlib.import_module("digest.orchestrator")
    importlib.import_module("digest.approver")


def test_orchestrator_has_main():
    mod = importlib.import_module("digest.orchestrator")
    assert hasattr(mod, "main")


def test_approver_has_main_and_handle_update():
    mod = importlib.import_module("digest.approver")
    assert hasattr(mod, "main")
    assert hasattr(mod, "handle_update")


def test_handle_update_clears_buttons_then_shows_loading_then_result():
    service = MagicMock(); service.apply.return_value = "✅ Published: T"
    tg = MagicMock()
    update = {
        "update_id": 1,
        "callback_query": {"id": "q1", "data": "pub:2026-06-16:s",
                           "message": {"message_id": 55}},
    }
    handle_update(update, service, tg)
    service.apply.assert_called_once_with("pub", "2026-06-16:s")
    # edited twice (no reply_markup arg -> Telegram clears the keyboard both times):
    # first a loading state (before the slow apply), then the final result.
    assert tg.edit_message_text.call_count == 2
    assert tg.edit_message_text.call_args_list[0].args == (55, "⏳ Đang xử lý…")
    assert tg.edit_message_text.call_args_list[1].args == (55, "✅ Published: T")


def test_handle_update_ignores_non_callback_updates():
    service = MagicMock(); tg = MagicMock()
    handle_update({"update_id": 2}, service, tg)
    service.apply.assert_not_called()
    tg.edit_message_text.assert_not_called()


def test_handle_update_handles_bad_callback_data_gracefully():
    service = MagicMock(); tg = MagicMock()
    update = {"update_id": 3,
              "callback_query": {"id": "q2", "data": "garbage", "message": {"message_id": 3}}}
    handle_update(update, service, tg)
    service.apply.assert_not_called()
    tg.edit_message_text.assert_called_once_with(3, "Unknown action")


def test_handle_update_survives_stale_callback_400():
    # answerCallbackQuery on an expired callback returns HTTP 400 -> TelegramError.
    # The decision is already applied; this must NOT propagate and kill the service.
    service = MagicMock(); service.apply.return_value = "✅ Published: T"
    tg = MagicMock()
    tg.answer_callback.side_effect = TelegramError("400 Bad Request")
    update = {
        "update_id": 4,
        "callback_query": {"id": "old", "data": "pub:2026-06-16:s",
                           "message": {"message_id": 7}},
    }
    handle_update(update, service, tg)  # must not raise
    service.apply.assert_called_once_with("pub", "2026-06-16:s")
    assert tg.edit_message_text.call_count == 2  # loading + final, both still attempted


def test_handle_update_survives_edit_failure():
    service = MagicMock(); service.apply.return_value = "ok"
    tg = MagicMock()
    tg.edit_message_text.side_effect = TelegramError("400")
    update = {
        "update_id": 5,
        "callback_query": {"id": "q", "data": "hold:2026-06-16:s",
                           "message": {"message_id": 9}},
    }
    handle_update(update, service, tg)  # must not raise
