"""Command handlers for the Python OpenSkills CLI."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import click

from .utils.agents_md import replace_skills_section
from .utils.dirs import DestinationInfo, get_search_dirs, resolve_destination
from .utils.errors import EXIT_GENERIC_ERROR, EXIT_OK, exit_with_error
from .utils.fs_ops import copy_skill_dir
from .utils.prompts import confirm_removal, prompt_for_removal_selection
from .utils.repo_service import WorkingCopy, prepare_skill_working_copy
from .utils.skill_validation import SkillDocument, load_skill_document
from .utils.skills import Skill, discover_skills, find_skill


@dataclass(frozen=True)
class SkillCandidate:
    name: str
    description: str
    path: Path


def _read_skill_document(path: Path) -> SkillDocument | None:
    try:
        return load_skill_document(path, strict=False)
    except Exception:
        return None


def _discover_skill_candidates(root: Path) -> list[SkillCandidate]:
    candidates: list[SkillCandidate] = []

    for skill_md in root.rglob("SKILL.md"):
        document = _read_skill_document(skill_md)
        if document is None:
            continue

        name = document.metadata.name or skill_md.parent.name
        description = document.metadata.description
        candidates.append(SkillCandidate(name=name, description=description, path=skill_md.parent))

    return candidates


def _select_candidates(candidates: Sequence[SkillCandidate], *, yes: bool) -> list[SkillCandidate]:
    if yes or len(candidates) <= 1:
        return list(candidates)

    selected: list[SkillCandidate] = []
    for candidate in candidates:
        if click.confirm(f"Install {candidate.name}?", default=True):
            selected.append(candidate)

    return selected


def _display_install_summary(result_label: str, dest: DestinationInfo) -> None:
    click.echo("")
    click.echo("Read skill: openskills read <skill-name>")
    if dest.scope == "project":
        click.echo("Sync to AGENTS.md: openskills sync")
    click.echo(result_label)


def install_skill_command(
    source: str,
    *,
    global_install: bool,
    universal: bool,
    yes: bool,
    temp_root: str | None = None,
) -> None:
    destination = resolve_destination(global_install=global_install, universal=universal)

    click.echo(f"Installing from: {source}")
    click.echo(f"Location: {destination.label}\n")

    working: WorkingCopy | None = None
    try:
        working = prepare_skill_working_copy(source, temp_root=temp_root)
    except Exception as exc:  # pragma: no cover - subprocess failures surfaced to user
        exit_with_error(str(exc))

    assert working is not None

    try:
        candidates = _discover_skill_candidates(Path(working.path))
        if not candidates:
            exit_with_error("No SKILL.md files found in source")

        selected = _select_candidates(candidates, yes=yes)
        if not selected:
            exit_with_error("No skills selected for installation", code=EXIT_OK)

        for candidate in selected:
            target_dir = destination.target_dir / candidate.name
            result = copy_skill_dir(
                str(candidate.path),
                str(target_dir),
                yes=yes,
                prompt=lambda message: click.confirm(message, default=False),
            )
            status = result.status
            if status == "skipped":
                click.echo(f"Skipped existing skill: {candidate.name}")
            elif status == "backed_up":
                click.echo(
                    f"Updated {candidate.name} -> {result.target_path} (backup: {result.backup_path})"
                )
            else:
                click.echo(f"Installed {candidate.name} -> {result.target_path}")

        _display_install_summary("", destination)
    finally:
        working.cleanup()


def _format_location(skill: Skill) -> str:
    return "project" if skill.location == "project" else "global"


def list_skills_command(*, cwd: Path | None = None, home: Path | None = None) -> None:
    skills = discover_skills(cwd=cwd, home=home)

    click.echo("Available Skills:\n")

    if not skills:
        click.echo("No skills installed.\n")
        click.echo("Install skills:")
        click.echo("  openskills install anthropics/skills         # Project (default)")
        click.echo("  openskills install owner/skill --global     # Global (advanced)")
        return

    sorted_skills = sorted(skills, key=lambda s: (s.location != "project", s.name.lower()))

    for skill in sorted_skills:
        label = "(project)" if skill.location == "project" else "(global)"
        click.echo(f"  {skill.name:25} {label}")
        click.echo(f"    {skill.description}\n")

    project_count = sum(1 for s in skills if s.location == "project")
    global_count = len(skills) - project_count
    click.echo(f"Summary: {project_count} project, {global_count} global ({len(skills)} total)")


def read_skill_command(skill_name: str, *, cwd: Path | None = None, home: Path | None = None) -> None:
    skill = find_skill(skill_name, cwd=cwd, home=home)
    if skill is None:
        searched = "\n".join(f"  {path}" for path in get_search_dirs(cwd=cwd, home=home))
        exit_with_error(
            "\n".join(
                [
                    f"Error: Skill '{skill_name}' not found",
                    "",
                    "Searched:",
                    searched,
                    "",
                    "Install skills: openskills install owner/repo",
                ]
            )
        )

    content = Path(skill.skill_path).read_text(encoding="utf-8")
    click.echo(f"Reading: {skill.name}")
    click.echo(f"Base directory: {skill.base_dir}")
    click.echo("")
    click.echo(content)
    click.echo("")
    click.echo(f"Skill read: {skill.name}")


def _choose_sync_skills(skills: Sequence[Skill], *, yes: bool) -> list[Skill]:
    if yes or len(skills) <= 1:
        return list(skills)

    chosen: list[Skill] = []
    for skill in skills:
        default = skill.location == "project"
        if click.confirm(f"Sync {skill.name} ({_format_location(skill)})?", default=default):
            chosen.append(skill)
    return chosen


def _parse_current_skill_names(content: str) -> set[str]:
    names: set[str] = set()
    marker_start = "<!-- SKILLS_TABLE_START -->"
    marker_end = "<!-- SKILLS_TABLE_END -->"

    if marker_start in content and marker_end in content:
        segment = content.split(marker_start, 1)[1].split(marker_end, 1)[0]
        for line in segment.splitlines():
            if line.strip().startswith("<name>") and line.strip().endswith("</name>"):
                names.add(line.replace("<name>", "").replace("</name>", "").strip())
    return names


def sync_agents_md_command(*, yes: bool, cwd: Path | None = None) -> None:
    agents_md = Path(cwd or Path.cwd()) / "AGENTS.md"
    if not agents_md.exists():
        click.echo("No AGENTS.md to update")
        return

    skills = discover_skills(cwd=cwd)
    if not skills:
        click.echo("No skills installed. Install skills first: openskills install anthropics/skills --project")
        return

    content = agents_md.read_text(encoding="utf-8")

    chosen = _choose_sync_skills(skills, yes=yes)
    if not chosen:
        agents_md.write_text(content, encoding="utf-8")
        click.echo("No skills selected; AGENTS.md left unchanged")
        return

    updated = replace_skills_section(content, chosen)
    agents_md.write_text(updated, encoding="utf-8")

    had_markers = "<skills_system" in content or "<!-- SKILLS_TABLE_START -->" in content
    message = "Synced" if had_markers else "Added skills section to"
    click.echo(f"✅ {message} AGENTS.md with {len(chosen)} skill(s)")


def _remove_skill_folder(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def manage_skills_command(*, yes: bool, cwd: Path | None = None, home: Path | None = None) -> None:
    skills = discover_skills(cwd=cwd, home=home)
    names = [skill.name for skill in skills]

    selections = prompt_for_removal_selection(names, yes=yes)
    if not confirm_removal(selections, yes=yes):
        click.echo("No skills removed")
        return

    for skill_name in selections:
        skill = find_skill(skill_name, cwd=cwd, home=home)
        if skill:
            _remove_skill_folder(skill.base_dir)
            click.echo(f"Removed {skill.name}")


def remove_skill_command(skill_name: str, *, cwd: Path | None = None, home: Path | None = None) -> None:
    skill = find_skill(skill_name, cwd=cwd, home=home)
    if skill is None:
        exit_with_error(f"Skill '{skill_name}' not found", code=EXIT_GENERIC_ERROR)

    _remove_skill_folder(skill.base_dir)
    click.echo(f"Removed {skill.name}")


__all__ = [
    "install_skill_command",
    "list_skills_command",
    "manage_skills_command",
    "read_skill_command",
    "remove_skill_command",
    "sync_agents_md_command",
]
