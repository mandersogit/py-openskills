"""Rendering and synchronization helpers for AGENTS.md skill tables."""

from __future__ import annotations

import re
from typing import Iterable, Sequence

from .skills import Skill

__all__ = [
    "render_usage_snippet",
    "render_available_skills_xml",
    "render_skills_system",
    "replace_skills_section",
]

_SKILLS_TABLE_START = "<!-- SKILLS_TABLE_START -->"
_SKILLS_TABLE_END = "<!-- SKILLS_TABLE_END -->"


def render_usage_snippet() -> str:
    """Return the static usage guidance block used inside <skills_system>."""

    return """<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge.

How to use skills:
- Invoke: Bash(\"openskills read <skill-name>\")
- The skill content will load with detailed instructions on how to complete the task
- Base directory provided in output for resolving bundled resources (references/, scripts/, assets/)

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
- Each skill invocation is stateless
</usage>"""


def _render_skill_entry(skill: Skill) -> str:
    return "\n".join(
        [
            "<skill>",
            f"<name>{skill.name}</name>",
            f"<description>{skill.description}</description>",
            f"<location>{skill.location}</location>",
            "</skill>",
        ]
    )


def render_available_skills_xml(skills: Sequence[Skill] | Iterable[Skill]) -> str:
    """Render the <available_skills> block matching the Node output."""

    entries = [_render_skill_entry(skill) for skill in skills]
    inner = "\n\n".join(entries)
    return f"<available_skills>\n\n{inner}\n\n</available_skills>"


def render_skills_system(skills: Sequence[Skill] | Iterable[Skill]) -> str:
    """Render the full <skills_system> XML payload."""

    usage = render_usage_snippet()
    available_skills = render_available_skills_xml(skills)

    return (
        "<skills_system priority=\"1\">\n\n"
        "## Available Skills\n\n"
        f"{_SKILLS_TABLE_START}\n"
        f"{usage}\n\n"
        f"{available_skills}\n"
        f"{_SKILLS_TABLE_END}\n\n"
        "</skills_system>"
    )


def replace_skills_section(content: str, skills: Sequence[Skill] | Iterable[Skill]) -> str:
    """Replace or append the skills section inside an AGENTS.md document."""

    new_section = render_skills_system(skills)

    if "<skills_system" in content:
        return re.sub(r"<skills_system[^>]*>[\s\S]*?</skills_system>", new_section, content, count=1)

    if _SKILLS_TABLE_START in content and _SKILLS_TABLE_END in content:
        inner = re.sub(r"</?skills_system[^>]*>", "", new_section).strip("\n")
        pattern = rf"{re.escape(_SKILLS_TABLE_START)}[\s\S]*?{re.escape(_SKILLS_TABLE_END)}"
        replacement = f"{_SKILLS_TABLE_START}\n{inner}\n{_SKILLS_TABLE_END}"
        return re.sub(pattern, replacement, content, count=1)

    stripped = content.rstrip()
    separator = "\n\n" if stripped else ""
    return f"{stripped}{separator}{new_section}\n"
