"""Validate and parse SKILL.md files with YAML frontmatter."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import warnings

import yaml


class SkillValidationError(Exception):
    """Raised when a SKILL.md file fails validation."""


@dataclass
class SkillMetadata:
    """Metadata defined in the SKILL.md YAML frontmatter."""

    name: str
    description: str
    context: Optional[str] = None


@dataclass
class SkillDocument:
    """Structured representation of a SKILL.md file."""

    path: Path
    metadata: SkillMetadata
    body: str


def load_skill_document(path: Path | str, *, strict: bool = True) -> Optional[SkillDocument]:
    """Load and validate a SKILL.md file.

    Args:
        path: Path to the SKILL.md file.
        strict: When True, raise :class:`SkillValidationError` on problems.
            When False, emit warnings and return ``None`` to allow lenient flows.

    Returns:
        SkillDocument if the file is valid, otherwise ``None`` when ``strict`` is False.
    """

    skill_path = Path(path)

    if not skill_path.exists():
        return _handle_error(f"SKILL.md not found at {skill_path}", strict)

    content = skill_path.read_text(encoding="utf-8")

    try:
        frontmatter, body = _split_frontmatter(content)
        metadata = _parse_frontmatter(frontmatter)
    except SkillValidationError as exc:  # pragma: no cover - propagated in strict
        return _handle_error(str(exc), strict)

    return SkillDocument(path=skill_path, metadata=metadata, body=body)


def _handle_error(message: str, strict: bool) -> Optional[SkillDocument]:
    if strict:
        raise SkillValidationError(message)

    warnings.warn(message, stacklevel=2)
    return None


def _split_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SkillValidationError("SKILL.md is missing YAML frontmatter start delimiter ('---')")

    closing_index = next((idx for idx, line in enumerate(lines[1:], start=1) if line.strip() == "---"), None)
    if closing_index is None:
        raise SkillValidationError("SKILL.md frontmatter is missing the closing '---' delimiter")

    frontmatter_text = "\n".join(lines[1:closing_index])
    body = "\n".join(lines[closing_index + 1 :])

    try:
        data = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - safety net for malformed YAML
        raise SkillValidationError(f"Invalid YAML frontmatter: {exc}") from exc

    if not isinstance(data, dict):
        raise SkillValidationError("SKILL.md frontmatter must be a mapping")

    return data, body


def _parse_frontmatter(frontmatter: Dict[str, Any]) -> SkillMetadata:
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    context = frontmatter.get("context")

    missing = [field for field in ["name", "description"] if not frontmatter.get(field)]
    if missing:
        raise SkillValidationError(f"SKILL.md frontmatter missing required field(s): {', '.join(missing)}")

    return SkillMetadata(name=str(name), description=str(description), context=str(context) if context else None)
