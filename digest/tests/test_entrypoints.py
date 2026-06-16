import importlib


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
