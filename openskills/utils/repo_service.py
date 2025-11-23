"""Git-backed repository helpers for skill working copies."""

import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

GitRunner = Callable[[Sequence[str], str | None], str]


@dataclass
class WorkingCopy:
    """Represents a temporary working copy of a repository."""

    path: str
    source: str
    commit: str | None
    cleanup: Callable[[], None]


def _run_git(args: Sequence[str], cwd: str | None = None) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def git_clone(repo: str, destination: Path, *, git_runner: GitRunner | None = None) -> None:
    runner = git_runner or _run_git
    runner(["clone", "--quiet", "--depth", "1", repo, str(destination)])


def git_fetch(cwd: Path, *, git_runner: GitRunner | None = None) -> None:
    runner = git_runner or _run_git
    runner(["fetch", "--quiet"], str(cwd))


def git_pull(cwd: Path, *, git_runner: GitRunner | None = None) -> None:
    runner = git_runner or _run_git
    runner(["pull", "--quiet"], str(cwd))


def _rev_parse_head(cwd: Path, *, git_runner: GitRunner | None = None) -> str:
    runner = git_runner or _run_git
    return runner(["rev-parse", "HEAD"], str(cwd))


def _normalize_source(source: str) -> tuple[str, bool]:
    expanded = os.path.expanduser(source)
    local_path = Path(expanded)
    if local_path.exists():
        return str(local_path.resolve()), True

    if "://" in source or source.startswith("git@"):
        return source, False

    return f"https://github.com/{source}", False


def _allocate_workdir(temp_root: str | None = None) -> tuple[Path, Path]:
    base_dir = Path(tempfile.mkdtemp(prefix="openskills-", dir=temp_root))
    working_dir = base_dir / "skill"
    return base_dir, working_dir


def prepare_skill_working_copy(
    source: str,
    *,
    temp_root: str | None = None,
    git_runner: GitRunner | None = None,
) -> WorkingCopy:
    normalized_source, is_local = _normalize_source(source)
    base_dir, working_dir = _allocate_workdir(temp_root)

    def _cleanup() -> None:
        shutil.rmtree(base_dir, ignore_errors=True)

    if is_local:
        shutil.copytree(normalized_source, working_dir)
    else:
        git_clone(normalized_source, working_dir, git_runner=git_runner)

    commit: str | None
    try:
        commit = _rev_parse_head(working_dir, git_runner=git_runner)
    except subprocess.CalledProcessError:
        commit = None

    return WorkingCopy(str(working_dir), normalized_source, commit, _cleanup)

