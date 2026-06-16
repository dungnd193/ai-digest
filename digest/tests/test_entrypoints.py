import importlib
from unittest.mock import MagicMock

from digest.approver import handle_update


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


def test_handle_update_applies_decision_and_acknowledges():
    service = MagicMock(); service.apply.return_value = "✅ Published: T"
    tg = MagicMock()
    update = {
        "update_id": 1,
        "callback_query": {"id": "q1", "data": "pub:2026-06-16:s",
                           "message": {"message_id": 55}},
    }
    handle_update(update, service, tg)
    service.apply.assert_called_once_with("pub", "2026-06-16:s")
    tg.answer_callback.assert_called_once()
    tg.edit_message_text.assert_called_once_with(55, "✅ Published: T")


def test_handle_update_ignores_non_callback_updates():
    service = MagicMock(); tg = MagicMock()
    handle_update({"update_id": 2}, service, tg)
    service.apply.assert_not_called()
    tg.answer_callback.assert_not_called()


def test_handle_update_handles_bad_callback_data_gracefully():
    service = MagicMock(); tg = MagicMock()
    update = {"update_id": 3, "callback_query": {"id": "q2", "data": "garbage"}}
    handle_update(update, service, tg)
    service.apply.assert_not_called()
    tg.answer_callback.assert_called_once()
