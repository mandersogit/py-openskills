from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Sequence

from openskills.utils.repo_service import prepare_skill_working_copy

GitRunner = Callable[[Sequence[str], str | None], str]


def _make_stub_runner(expected_commit: str, calls: list[tuple[list[str], str | None]]) -> GitRunner:
    def _runner(args: Sequence[str], cwd: str | None = None) -> str:
        calls.append((list(args), cwd))
        if args and args[0] == "clone":
            target_dir = Path(args[-1])
            target_dir.mkdir(parents=True, exist_ok=True)
            (target_dir / ".git").mkdir(parents=True, exist_ok=True)
            return ""
        if args[:2] == ["rev-parse", "HEAD"]:
            return expected_commit
        return ""

    return _runner


def test_prepare_skill_working_copy_resolves_shorthand_and_clones_https(tmp_path: Path) -> None:
    calls: list[tuple[list[str], str | None]] = []
    runner = _make_stub_runner("abcdef1234567890", calls)

    result = prepare_skill_working_copy("owner/repo", temp_root=str(tmp_path), git_runner=runner)

    assert calls[0][0][:4] == ["clone", "--quiet", "--depth", "1"]
    assert calls[0][0][4] == "https://github.com/owner/repo"
    assert Path(calls[0][0][-1]).is_dir()
    assert result.source == "https://github.com/owner/repo"
    assert result.commit == "abcdef1234567890"

    result.cleanup()
    assert not Path(result.path).exists()


def test_prepare_skill_working_copy_supports_ssh_and_https_urls(tmp_path: Path) -> None:
    calls: list[tuple[list[str], str | None]] = []
    runner = _make_stub_runner("deadbeef", calls)

    ssh_result = prepare_skill_working_copy("git@github.com:owner/repo.git", temp_root=str(tmp_path), git_runner=runner)
    https_result = prepare_skill_working_copy("https://example.com/owner/repo.git", temp_root=str(tmp_path), git_runner=runner)

    assert ["clone", "--quiet", "--depth", "1", "git@github.com:owner/repo.git", ssh_result.path] in [call[0] for call in calls]
    assert [
        "clone",
        "--quiet",
        "--depth",
        "1",
        "https://example.com/owner/repo.git",
        https_result.path,
    ] in [call[0] for call in calls]

    ssh_result.cleanup()
    https_result.cleanup()


def test_prepare_skill_working_copy_copies_local_repository(tmp_path: Path) -> None:
    repo_dir = Path(tempfile.mkdtemp(prefix="openskills-local-", dir=tmp_path))
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    (repo_dir / "README.md").write_text("# Test repo\n", encoding="utf-8")

    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Test User",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test User",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, env=env)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo_dir, check=True, env=env)

    working_copy = prepare_skill_working_copy(str(repo_dir), temp_root=str(tmp_path))

    assert Path(working_copy.path) != repo_dir
    assert (Path(working_copy.path) / "README.md").exists()
    assert re.fullmatch(r"[a-f0-9]{7,}", working_copy.commit)

    working_copy.cleanup()
    assert not Path(working_copy.path).exists()

