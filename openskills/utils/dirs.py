"""Directory resolution helpers for skill installation roots."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


def _as_path(value: Path | str | None, *, default: Path) -> Path:
    """Coerce an optional pathlike value to :class:`Path` with a fallback."""

    if value is None:
        return default

    return value if isinstance(value, Path) else Path(value)


def get_skills_dir(
    *,
    project_local: bool = False,
    universal: bool = False,
    cwd: Path | str | None = None,
    home_dir: Path | str | None = None,
) -> Path:
    """Return the directory where skills should be installed.

    Mirrors the Node implementation: defaults to the global Claude directory,
    with optional project-local and universal (.agent) modes.
    """

    cwd_path = _as_path(cwd, default=Path.cwd())
    home_path = _as_path(home_dir, default=Path.home())

    base_dir = cwd_path if project_local else home_path
    folder = ".agent/skills" if universal else ".claude/skills"
    return base_dir / folder


def _resolve_home_path(home_dir: Path | str | None, home: Path | str | None) -> Path:
    """Select and normalize the home directory hint.

    Supports both the legacy ``home_dir`` keyword and the newer ``home`` keyword
    used by other utilities. ``home`` takes precedence when both are supplied.
    """

    selected = home if home is not None else home_dir
    return _as_path(selected, default=Path.home())


def get_search_dirs(
    *,
    cwd: Path | str | None = None,
    home_dir: Path | str | None = None,
    home: Path | str | None = None,
) -> list[Path]:
    """Return all searchable skill roots in priority order.

    Priority: project .agent, global .agent, project .claude, global .claude.
    """

    cwd_path = _as_path(cwd, default=Path.cwd())
    home_path = _resolve_home_path(home_dir, home)

    return [
        cwd_path / ".agent/skills",  # 1. Project universal (.agent)
        home_path / ".agent/skills",  # 2. Global universal (.agent)
        cwd_path / ".claude/skills",  # 3. Project claude
        home_path / ".claude/skills",  # 4. Global claude
    ]


@dataclass(frozen=True)
class DestinationInfo:
    target_dir: Path
    folder: Literal[".claude/skills", ".agent/skills"]
    scope: Literal["project", "global"]
    label: str


def resolve_destination(
    *,
    global_install: bool = False,
    universal: bool = False,
    cwd: Path | str | None = None,
    home_dir: Path | str | None = None,
) -> DestinationInfo:
    """Resolve the destination directory based on installation flags."""

    folder: Literal[".claude/skills", ".agent/skills"] = ".agent/skills" if universal else ".claude/skills"
    scope: Literal["project", "global"] = "global" if global_install else "project"

    cwd_path = _as_path(cwd, default=Path.cwd())
    home_path = _as_path(home_dir, default=Path.home())
    base_dir = home_path if scope == "global" else cwd_path

    target_dir = base_dir / folder
    label = f"{scope} ({folder})" if scope == "project" else f"global (~/{folder})"

    return DestinationInfo(target_dir=target_dir, folder=folder, scope=scope, label=label)


__all__ = ["get_skills_dir", "get_search_dirs", "DestinationInfo", "resolve_destination"]
