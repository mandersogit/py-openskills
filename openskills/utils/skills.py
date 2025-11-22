"""Skill discovery utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .dirs import get_search_dirs
from .yaml import extract_yaml_field

__all__ = ["Skill", "discover_skills", "find_skill"]


@dataclass(frozen=True)
class Skill:
    """Representation of an installed skill."""

    name: str
    description: str
    location: str
    base_dir: Path
    skill_path: Path


def _is_relative_to(base: Path, target: Path) -> bool:
    """Return True if ``target`` is within ``base`` (uses Python 3.11+ Path helpers)."""

    return target.is_relative_to(base)


def discover_skills(*, cwd: Path | None = None, home: Path | None = None) -> list[Skill]:
    """Find all installed skills across search roots.

    Deduplicates by skill name, honoring search priority to mirror Node output.
    """

    cwd = Path.cwd() if cwd is None else cwd
    search_dirs = get_search_dirs(cwd=cwd, home=home)

    skills: list[Skill] = []
    seen: set[str] = set()

    for directory in search_dirs:
        if not directory.is_dir():
            continue

        for entry in sorted(directory.iterdir(), key=lambda p: p.name):
            if not entry.is_dir():
                continue

            skill_name = entry.name
            if skill_name in seen:
                continue

            skill_md = entry / "SKILL.md"
            if not skill_md.is_file():
                continue

            content = skill_md.read_text(encoding="utf-8")
            description = extract_yaml_field(content, "description")

            location = "project" if _is_relative_to(cwd, directory) else "global"

            skills.append(
                Skill(
                    name=skill_name,
                    description=description,
                    location=location,
                    base_dir=entry,
                    skill_path=skill_md,
                )
            )
            seen.add(skill_name)

    return skills


def find_skill(skill_name: str, *, cwd: Path | None = None, home: Path | None = None) -> Skill | None:
    """Find the first matching skill across search roots."""

    cwd = Path.cwd() if cwd is None else cwd

    for directory in get_search_dirs(cwd=cwd, home=home):
        skill_md = directory / skill_name / "SKILL.md"
        if skill_md.is_file():
            location = "project" if _is_relative_to(cwd, directory) else "global"
            return Skill(
                name=skill_name,
                description=extract_yaml_field(skill_md.read_text(encoding="utf-8"), "description"),
                location=location,
                base_dir=directory / skill_name,
                skill_path=skill_md,
            )

    return None
