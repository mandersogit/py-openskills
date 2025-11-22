"""Utility helpers for the OpenSkills CLI."""

from .agents_md import (
    render_available_skills_xml,
    render_skills_system,
    render_usage_snippet,
    replace_skills_section,
)
from .dirs import DestinationInfo, get_search_dirs, get_skills_dir, resolve_destination
from .errors import EXIT_GENERIC_ERROR, EXIT_NOT_IMPLEMENTED, EXIT_OK, exit_not_implemented, exit_with_error
from .fs_ops import TransferResult, backup_skill_dir, copy_skill_dir, move_skill_dir
from .prompts import confirm_removal, prompt_for_removal_selection
from .repo_service import WorkingCopy, git_clone, git_fetch, git_pull, prepare_skill_working_copy
from .skill_validation import SkillDocument, SkillMetadata, SkillValidationError, load_skill_document
from .skills import Skill, discover_skills, find_skill
from .yaml import extract_yaml_field, has_valid_frontmatter

__all__ = [
    "EXIT_GENERIC_ERROR",
    "EXIT_NOT_IMPLEMENTED",
    "EXIT_OK",
    "DestinationInfo",
    "TransferResult",
    "WorkingCopy",
    "Skill",
    "SkillDocument",
    "SkillMetadata",
    "SkillValidationError",
    "confirm_removal",
    "backup_skill_dir",
    "copy_skill_dir",
    "discover_skills",
    "exit_not_implemented",
    "exit_with_error",
    "extract_yaml_field",
    "find_skill",
    "get_search_dirs",
    "get_skills_dir",
    "git_clone",
    "git_fetch",
    "git_pull",
    "has_valid_frontmatter",
    "load_skill_document",
    "move_skill_dir",
    "prepare_skill_working_copy",
    "prompt_for_removal_selection",
    "render_available_skills_xml",
    "render_skills_system",
    "render_usage_snippet",
    "replace_skills_section",
    "resolve_destination",
]
