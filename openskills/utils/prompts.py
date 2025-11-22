"""Prompt helpers that gracefully degrade when optional dependencies are missing."""

import importlib
import importlib.util
from collections.abc import Iterable, Sequence

import click


def _load_questionary():
    """Return the ``questionary`` module if it is installed.

    The helper avoids import-time failures for environments where the optional
    dependency is not present. When absent, callers can fall back to
    non-interactive defaults.
    """

    spec = importlib.util.find_spec("questionary")
    if spec is None:
        return None

    return importlib.import_module("questionary")


def prompt_for_removal_selection(
    available: Sequence[str], *, yes: bool = False
) -> list[str]:
    """Prompt for which skills to remove using ``questionary`` when available.

    When ``yes`` is ``True``, all available skills are selected without
    prompting. If ``questionary`` is not installed, the function skips prompts
    and returns an empty selection while emitting a notice so automation can
    rely on deterministic output and exit codes.
    """

    if yes:
        return list(available)

    if not available:
        return []

    questionary = _load_questionary()
    if questionary is None:
        click.echo(
            "questionary not installed; skipping interactive removal prompts and "
            "defaulting to no selection."
        )
        return []

    answer = questionary.checkbox(
        "Select skills to remove",
        choices=list(available),
    ).ask()

    if answer is None:
        return []

    return list(answer)


def confirm_removal(selections: Iterable[str], *, yes: bool = False) -> bool:
    """Confirm removal for the provided selections.

    The confirmation prompt uses ``questionary`` when present. If the optional
    dependency is unavailable, the function defaults to a safe ``False``
    response while preserving the standard messaging expected by automation.
    """

    chosen = list(selections)

    if yes:
        return bool(chosen)

    if not chosen:
        return False

    questionary = _load_questionary()
    if questionary is None:
        click.echo(
            "questionary not installed; removal not confirmed. Re-run with --yes "
            "to force non-interactive removal."
        )
        return False

    prompt = questionary.confirm(
        f"Remove {len(chosen)} skill(s)?", default=False
    ).ask()

    return bool(prompt)
