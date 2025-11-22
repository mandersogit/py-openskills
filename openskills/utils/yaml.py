"""Minimal YAML helpers for parsing SKILL.md frontmatter."""

import re

__all__ = ["extract_yaml_field", "has_valid_frontmatter"]


FRONTMATTER_PREFIX = "---"


def extract_yaml_field(content: str, field: str) -> str:
    """Extract a simple field from YAML frontmatter using a lightweight regex."""

    match = re.search(rf"^{re.escape(field)}:\s*(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def has_valid_frontmatter(content: str) -> bool:
    """Check whether the provided content starts with YAML frontmatter."""

    return content.strip().startswith(FRONTMATTER_PREFIX)
