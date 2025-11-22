"""Shared helpers for consistent exit handling."""

from __future__ import annotations

from typing import NoReturn

import click

EXIT_OK = 0
EXIT_GENERIC_ERROR = 1
EXIT_NOT_IMPLEMENTED = 99


def exit_with_error(message: str, *, code: int = EXIT_GENERIC_ERROR) -> NoReturn:
    """Print an error message and exit with the provided code."""
    click.echo(message, err=True)
    raise SystemExit(code)


def exit_not_implemented(command_name: str) -> NoReturn:
    """Exit with a standard not-implemented message for stubbed commands."""
    exit_with_error(
        f"Command '{command_name}' is not implemented yet.", code=EXIT_NOT_IMPLEMENTED
    )
