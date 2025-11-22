from __future__ import annotations

from pathlib import Path

import pytest

from openskills.utils import (
    Skill,
    discover_skills,
    render_skills_system,
    replace_skills_section,
)


def _write_skill(root: Path, name: str, description: str) -> None:
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n",
        encoding="utf-8",
    )


def _sample_skills() -> list[Skill]:
    return [
        Skill(
            name="alpha",
            description="First skill description",
            location="project",
            base_dir=Path("/project/.agent/skills/alpha"),
            skill_path=Path("/project/.agent/skills/alpha/SKILL.md"),
        ),
        Skill(
            name="beta",
            description="Second skill description",
            location="global",
            base_dir=Path("/home/.claude/skills/beta"),
            skill_path=Path("/home/.claude/skills/beta/SKILL.md"),
        ),
    ]


def test_discover_skills_scans_all_roots(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    home_root = tmp_path / "home"
    project_root.mkdir()
    home_root.mkdir()

    project_agent = project_root / ".agent/skills"
    global_agent = home_root / ".agent/skills"
    project_claude = project_root / ".claude/skills"
    global_claude = home_root / ".claude/skills"

    _write_skill(project_agent, "alpha", "Alpha project description")
    _write_skill(global_agent, "beta", "Beta global description")
    _write_skill(project_claude, "gamma", "Gamma project description")
    _write_skill(global_claude, "delta", "Delta global description")
    _write_skill(global_claude, "gamma", "Duplicate gamma")

    monkeypatch.chdir(project_root)

    skills = discover_skills(cwd=project_root, home=home_root)

    assert [skill.name for skill in skills] == ["alpha", "beta", "gamma", "delta"]
    assert [skill.location for skill in skills] == ["project", "global", "project", "global"]

    assert skills[0].base_dir == project_agent / "alpha"
    assert skills[0].skill_path == project_agent / "alpha" / "SKILL.md"
    assert skills[1].base_dir == global_agent / "beta"
    assert skills[2].skill_path == project_claude / "gamma" / "SKILL.md"
    assert skills[3].base_dir == global_claude / "delta"

    assert skills[0].description == "Alpha project description"
    assert skills[1].description == "Beta global description"


def test_render_skills_system_matches_golden() -> None:
    skills = _sample_skills()
    rendered = render_skills_system(skills)

    expected = Path("tests/python/fixtures/goldens/skills_system.xml").read_text(encoding="utf-8").rstrip("\n")
    assert rendered == expected


def test_replace_skills_section_matches_golden() -> None:
    skills = _sample_skills()
    content = Path("tests/python/fixtures/agents_with_markers.md").read_text(encoding="utf-8")

    updated = replace_skills_section(content, skills)
    expected = Path("tests/python/fixtures/goldens/agents_sync_with_markers.md").read_text(encoding="utf-8")

    assert updated == expected
