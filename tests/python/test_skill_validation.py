import warnings
from pathlib import Path

import pytest

from openskills.utils import (
    SkillDocument,
    SkillMetadata,
    SkillValidationError,
    load_skill_document,
)


FIXTURES = Path(__file__).parent / "fixtures" / "skills"


def test_load_skill_document_returns_dataclasses() -> None:
    skill_path = FIXTURES / "valid" / "SKILL.md"

    result = load_skill_document(skill_path)

    assert isinstance(result, SkillDocument)
    assert result.path == skill_path
    assert isinstance(result.metadata, SkillMetadata)
    assert result.metadata.name == "example-skill"
    assert result.metadata.description == "Valid skill for testing"
    assert result.metadata.context == "Helpful notes"
    assert "Example Skill" in result.body


def test_missing_file_strict_raises() -> None:
    missing_path = FIXTURES / "missing" / "SKILL.md"

    with pytest.raises(SkillValidationError):
        load_skill_document(missing_path)


def test_missing_file_lenient_warns() -> None:
    missing_path = FIXTURES / "missing" / "SKILL.md"

    with warnings.catch_warnings(record=True) as caught:
        result = load_skill_document(missing_path, strict=False)

    assert result is None
    assert any("not found" in str(w.message) for w in caught)


def test_invalid_frontmatter_strict_failure() -> None:
    invalid_path = FIXTURES / "invalid_no_frontmatter" / "SKILL.md"

    with pytest.raises(SkillValidationError):
        load_skill_document(invalid_path)


def test_invalid_frontmatter_lenient_returns_none() -> None:
    invalid_path = FIXTURES / "invalid_no_frontmatter" / "SKILL.md"

    with warnings.catch_warnings(record=True) as caught:
        result = load_skill_document(invalid_path, strict=False)

    assert result is None
    assert any("frontmatter" in str(w.message) for w in caught)


def test_missing_required_fields() -> None:
    invalid_path = FIXTURES / "invalid_missing_fields" / "SKILL.md"

    with pytest.raises(SkillValidationError):
        load_skill_document(invalid_path)


