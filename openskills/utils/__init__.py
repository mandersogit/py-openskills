"""Utility helpers for the OpenSkills CLI."""

from .dirs import DestinationInfo, get_search_dirs, get_skills_dir, resolve_destination
from .errors import EXIT_GENERIC_ERROR, EXIT_NOT_IMPLEMENTED, EXIT_OK, exit_not_implemented, exit_with_error
from .fs_ops import TransferResult, backup_skill_dir, copy_skill_dir, move_skill_dir
from .agents_md import (
    render_available_skills_xml,
    render_skills_system,
    render_usage_snippet,
    replace_skills_section,
)
from .dirs import get_search_dirs, get_skills_dir
from .errors import EXIT_GENERIC_ERROR, EXIT_NOT_IMPLEMENTED, EXIT_OK, exit_not_implemented, exit_with_error
from .repo_service import (
    WorkingCopy,
    git_clone,
    git_fetch,
    git_pull,
    prepare_skill_working_copy,
)
from .skill_validation import (
    SkillDocument,
    SkillMetadata,
    SkillValidationError,
    load_skill_document,
)
from .skills import Skill, discover_skills, find_skill
from .yaml import extract_yaml_field, has_valid_frontmatter
from .prompts import confirm_removal, prompt_for_removal_selection

__all__ = [
    "EXIT_GENERIC_ERROR",
    "EXIT_NOT_IMPLEMENTED",
    "EXIT_OK",
    "DestinationInfo",
    "TransferResult",
    "backup_skill_dir",
    "copy_skill_dir",
    "get_search_dirs",
    "get_skills_dir",
    "move_skill_dir",
    "resolve_destination",
    "WorkingCopy",
    "exit_not_implemented",
    "exit_with_error",
    "git_clone",
    "git_fetch",
    "git_pull",
    "prepare_skill_working_copy",
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
    "SkillDocument",
    "SkillMetadata",
    "SkillValidationError",
    "load_skill_document",
    "confirm_removal",
    "prompt_for_removal_selection",
]
