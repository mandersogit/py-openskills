"""Utility helpers for the OpenSkills CLI."""

from .agents_md import (
    render_available_skills_xml,
    render_skills_system,
    render_usage_snippet,
    replace_skills_section,
)
from .dirs import get_search_dirs, get_skills_dir
from .errors import EXIT_GENERIC_ERROR, EXIT_NOT_IMPLEMENTED, EXIT_OK, exit_not_implemented, exit_with_error
from .skills import Skill, discover_skills, find_skill
from .yaml import extract_yaml_field, has_valid_frontmatter
from .prompts import confirm_removal, prompt_for_removal_selection

__all__ = [
    "EXIT_GENERIC_ERROR",
    "EXIT_NOT_IMPLEMENTED",
    "EXIT_OK",
    "Skill",
    "discover_skills",
    "extract_yaml_field",
    "find_skill",
    "get_search_dirs",
    "get_skills_dir",
    "has_valid_frontmatter",
    "render_available_skills_xml",
    "render_skills_system",
    "render_usage_snippet",
    "replace_skills_section",
    "exit_not_implemented",
    "exit_with_error",
    "confirm_removal",
    "prompt_for_removal_selection",
]
