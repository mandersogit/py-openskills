import re

import pytest
from click.testing import CliRunner

from openskills import __version__
from openskills.cli import cli


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_root_help_lists_commands(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    for command in ["install", "list", "read", "sync", "manage", "remove", "rm"]:
        assert command in result.output


def test_version_option_reports_version(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.output


def test_install_help_includes_flags(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["install", "--help"])

    assert result.exit_code == 0
    assert "-g, --global" in result.output
    assert "-u, --universal" in result.output
    assert "-y, --yes" in result.output
    assert "SOURCE" in result.output.upper()


def test_sync_help_includes_yes_flag(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["sync", "--help"])

    assert result.exit_code == 0
    assert "-y, --yes" in result.output


def test_remove_alias_help(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["rm", "--help"])

    assert result.exit_code == 0
    assert re.search(r"remove.*rm", result.output, re.IGNORECASE)
