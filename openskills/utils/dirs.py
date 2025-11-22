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
