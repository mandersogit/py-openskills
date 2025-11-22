from __future__ import annotations

import os
import subprocess
from pathlib import Path

from click.testing import CliRunner

from openskills.cli import cli


def _write_skill(path: Path, name: str, description: str, body: str = "") -> None:
    skill_dir = path / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_dir.joinpath("SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n{body}\n",
        encoding="utf-8",
    )


def _create_git_repo(base: Path) -> Path:
    repo = base / "skills-repo"
    repo.mkdir()
    _write_skill(repo, "skill-one", "Skill one description", "Details for one")
    nested = repo / "nested"
    nested.mkdir()
    _write_skill(nested, "skill-two", "Skill two description", "Details for two")

    git_env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }

    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=git_env)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, env=git_env)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, env=git_env)
    return repo


def test_install_list_read_and_sync(monkeypatch) -> None:
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        tmp_path = Path(tmp)
        env = {
            "HOME": str(tmp_path / "home"),
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        }
        repo = _create_git_repo(tmp_path)

        result = runner.invoke(cli, ["install", str(repo), "--yes"], env=env)
        assert result.exit_code == 0, result.output

        skill_one = tmp_path / ".claude/skills/skill-one/SKILL.md"
        skill_two = tmp_path / ".claude/skills/skill-two/SKILL.md"
        assert skill_one.exists()
        assert skill_two.exists()

        list_result = runner.invoke(cli, ["list"], env=env)
        assert list_result.exit_code == 0
        assert "skill-one" in list_result.output
        assert "skill-two" in list_result.output
        assert "Summary: 2 project, 0 global (2 total)" in list_result.output

        read_result = runner.invoke(cli, ["read", "skill-one"], env=env)
        assert read_result.exit_code == 0
        assert "Reading: skill-one" in read_result.output
        assert "Details for one" in read_result.output
        assert "Skill read: skill-one" in read_result.output

        agents_md = Path("AGENTS.md")
        agents_md.write_text("Intro", encoding="utf-8")

        sync_result = runner.invoke(cli, ["sync", "--yes"], env=env)
        assert sync_result.exit_code == 0
        synced = agents_md.read_text(encoding="utf-8")
        assert "<skills_system" in synced
        assert "<name>skill-one</name>" in synced
        assert "<name>skill-two</name>" in synced


def test_manage_and_remove(monkeypatch) -> None:
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        tmp_path = Path(tmp)
        env = {"HOME": str(tmp_path / "home")}

        skills_root = tmp_path / ".claude/skills"
        _write_skill(skills_root, "keep-me", "Stay put")
        _write_skill(skills_root, "remove-me", "Remove me")

        monkeypatch.setattr(
            "openskills.operations.prompt_for_removal_selection",
            lambda available, yes=False: ["remove-me"],
        )
        monkeypatch.setattr(
            "openskills.operations.confirm_removal",
            lambda selections, yes=False: True,
        )

        manage_result = runner.invoke(cli, ["manage"], env=env)
        assert manage_result.exit_code == 0
        assert not (skills_root / "remove-me").exists()
        assert (skills_root / "keep-me").exists()

        remove_result = runner.invoke(cli, ["remove", "keep-me"], env=env)
        assert remove_result.exit_code == 0
        assert not (skills_root / "keep-me").exists()

        missing_result = runner.invoke(cli, ["remove", "missing"], env=env)
        assert missing_result.exit_code != 0
        assert "Skill 'missing' not found" in missing_result.output
