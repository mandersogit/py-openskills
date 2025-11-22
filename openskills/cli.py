"""Command-line interface for the OpenSkills Python port."""

from __future__ import annotations

import click

from . import __version__
from .utils import exit_not_implemented

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def _stub(command_name: str) -> None:
    """Temporary stub used while functionality is implemented elsewhere."""
    exit_not_implemented(command_name)


@click.group(
    context_settings=CONTEXT_SETTINGS,
    help="Universal skills loader for AI coding agents",
)
@click.version_option(__version__, "--version", "-V")
def cli() -> None:
    """OpenSkills CLI entry point."""


@cli.command(name="list", help="List all installed skills")
def list_skills() -> None:
    _stub("list")


@cli.command(name="install", help="Install skill from GitHub or Git URL")
@click.argument("source")
@click.option("global_install", "-g", "--global", is_flag=True, help="Install globally (default: project install)")
@click.option(
    "universal",
    "-u",
    "--universal",
    is_flag=True,
    help="Install to .agent/skills/ (for universal AGENTS.md usage)",
)
@click.option(
    "yes",
    "-y",
    "--yes",
    is_flag=True,
    help="Skip interactive selection, install all skills found",
)
def install(source: str, *, global_install: bool, universal: bool, yes: bool) -> None:
    _stub("install")


@cli.command(name="read", help="Read skill to stdout (for AI agents)")
@click.argument("skill_name")
def read(skill_name: str) -> None:
    _stub("read")


@cli.command(
    name="sync",
    help="Update AGENTS.md with installed skills (interactive, pre-selects current state)",
)
@click.option("yes", "-y", "--yes", is_flag=True, help="Skip interactive selection, sync all skills")
def sync(yes: bool) -> None:
    _stub("sync")


@cli.command(name="manage", help="Interactively manage (remove) installed skills")
def manage() -> None:
    _stub("manage")


@cli.command(
    name="remove",
    help="Remove specific skill (alias: rm) (for scripts, use manage for interactive)",
)
@click.argument("skill_name")
def remove(skill_name: str) -> None:
    _stub("remove")


# Register the short alias after definition to keep Click compatibility.
cli.add_command(remove, "rm")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
