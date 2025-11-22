import importlib
import sys
from types import SimpleNamespace

import pytest

from openskills.utils import confirm_removal, prompt_for_removal_selection


@pytest.fixture()
def disable_questionary(monkeypatch: pytest.MonkeyPatch):
    """Ensure ``questionary`` is treated as missing for a test."""

    real_find_spec = importlib.util.find_spec

    def _missing_questionary(name: str):
        if name == "questionary":
            return None
        return real_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", _missing_questionary)
    monkeypatch.setitem(sys.modules, "questionary", None)


@pytest.fixture()
def fake_questionary(monkeypatch: pytest.MonkeyPatch):
    """Provide a controllable ``questionary`` stub for interactive paths."""

    prompts: dict[str, list[dict[str, object]]] = {"checkbox": [], "confirm": []}

    class _Answer:
        def __init__(self, response):
            self._response = response

        def ask(self):
            return self._response

    class _Questionary(SimpleNamespace):
        def checkbox(self, message: str, choices: list[str]):
            prompts["checkbox"].append({"message": message, "choices": choices})
            return _Answer(["beta"])

        def confirm(self, message: str, default: bool = False):
            prompts["confirm"].append({"message": message, "default": default})
            return _Answer(True)

    stub = _Questionary()
    real_find_spec = importlib.util.find_spec

    def _present_questionary(name: str):
        if name == "questionary":
            return object()
        return real_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", _present_questionary)
    monkeypatch.setitem(sys.modules, "questionary", stub)

    return prompts


def test_selection_uses_questionary_when_present(fake_questionary):
    selections = prompt_for_removal_selection(["alpha", "beta"], yes=False)

    assert selections == ["beta"]
    assert fake_questionary["checkbox"] == [
        {"message": "Select skills to remove", "choices": ["alpha", "beta"]}
    ]


def test_selection_defaults_to_all_when_yes_flag():
    selections = prompt_for_removal_selection(["alpha", "beta"], yes=True)

    assert selections == ["alpha", "beta"]


def test_selection_falls_back_without_questionary(disable_questionary, capsys):
    selections = prompt_for_removal_selection(["alpha", "beta"], yes=False)

    assert selections == []
    captured = capsys.readouterr().out
    assert "questionary not installed" in captured


def test_confirmation_uses_questionary_when_present(fake_questionary):
    confirmed = confirm_removal(["alpha", "beta"], yes=False)

    assert confirmed is True
    assert fake_questionary["confirm"] == [
        {"message": "Remove 2 skill(s)?", "default": False}
    ]


def test_confirmation_respects_yes_flag_with_selection():
    confirmed = confirm_removal(["alpha"], yes=True)

    assert confirmed is True


def test_confirmation_declines_without_questionary(disable_questionary, capsys):
    confirmed = confirm_removal(["alpha", "beta"], yes=False)

    assert confirmed is False
    captured = capsys.readouterr().out
    assert "removal not confirmed" in captured

