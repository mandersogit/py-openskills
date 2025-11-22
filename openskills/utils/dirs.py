"""Directory resolution helpers for skill installation targets."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal, Optional


def get_skills_dir(
    *, project_local: bool = False, universal: bool = False, cwd: Optional[str] = None, home_dir: Optional[str] = None
) -> str:
    """Return the skills directory path for the requested scope and type."""

    base_dir = (cwd or os.getcwd()) if project_local else (home_dir or os.path.expanduser("~"))
    folder = ".agent/skills" if universal else ".claude/skills"
    return os.path.join(base_dir, folder)


def get_search_dirs(*, cwd: Optional[str] = None, home_dir: Optional[str] = None) -> list[str]:
    """Return searchable skill directories in priority order."""

    current = cwd or os.getcwd()
    home = home_dir or os.path.expanduser("~")

    return [
        os.path.join(current, ".agent/skills"),
        os.path.join(home, ".agent/skills"),
        os.path.join(current, ".claude/skills"),
        os.path.join(home, ".claude/skills"),
    ]


@dataclass(frozen=True)
class DestinationInfo:
    target_dir: str
    folder: Literal[".claude/skills", ".agent/skills"]
    scope: Literal["project", "global"]
    label: str


def resolve_destination(
    *, global_install: bool = False, universal: bool = False, cwd: Optional[str] = None, home_dir: Optional[str] = None
) -> DestinationInfo:
    """Resolve the destination directory based on installation flags."""

    folder: Literal[".claude/skills", ".agent/skills"] = ".agent/skills" if universal else ".claude/skills"
    scope: Literal["project", "global"] = "global" if global_install else "project"

    current = cwd or os.getcwd()
    home = home_dir or os.path.expanduser("~")
    base_dir = home if scope == "global" else current

    target_dir = os.path.join(base_dir, folder)
    label = f"{scope} ({folder})" if scope == "project" else f"global (~/{folder})"

    return DestinationInfo(target_dir=target_dir, folder=folder, scope=scope, label=label)
"""Directory resolution helpers for skill installation roots."""

from __future__ import annotations

from pathlib import Path
from typing import List


def get_skills_dir(
    *, project_local: bool = False, universal: bool = False, cwd: Path | None = None, home: Path | None = None
) -> Path:
    """Return the directory where skills should be installed.

    Mirrors the Node implementation: defaults to the global Claude directory,
    with optional project-local and universal (.agent) modes.
    """

    cwd = Path.cwd() if cwd is None else cwd
    home = Path.home() if home is None else home

    base_dir = cwd if project_local else home
    folder = ".agent/skills" if universal else ".claude/skills"
    return base_dir / folder


def get_search_dirs(*, cwd: Path | None = None, home: Path | None = None) -> List[Path]:
    """Return all searchable skill roots in priority order.

    Priority: project .agent, global .agent, project .claude, global .claude.
    """

    cwd = Path.cwd() if cwd is None else cwd
    home = Path.home() if home is None else home

    return [
        cwd / ".agent/skills",  # 1. Project universal (.agent)
        home / ".agent/skills",  # 2. Global universal (.agent)
        cwd / ".claude/skills",  # 3. Project claude
        home / ".claude/skills",  # 4. Global claude
    ]


__all__ = ["get_skills_dir", "get_search_dirs"]
