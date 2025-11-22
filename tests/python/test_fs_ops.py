import os

from openskills.utils import copy_skill_dir


def test_copy_skill_dir_skips_when_prompt_declines(tmp_path) -> None:
    source_dir = tmp_path / "source"
    target_dir = tmp_path / "target"
    source_dir.mkdir()
    target_dir.mkdir()

    (source_dir / "file.txt").write_text("new-content")
    (target_dir / "file.txt").write_text("existing-content")

    prompts: list[str] = []

    def prompt(message: str) -> bool:
        prompts.append(message)
        return False

    result = copy_skill_dir(str(source_dir), str(target_dir), prompt=prompt)

    assert result.status == "skipped"
    assert prompts == [f"Skill already exists at {target_dir}. Overwrite?"]
    assert (target_dir / "file.txt").read_text() == "existing-content"


def test_copy_skill_dir_backs_up_when_yes(tmp_path) -> None:
    source_dir = tmp_path / "source"
    target_dir = tmp_path / "target"
    source_dir.mkdir()
    target_dir.mkdir()

    (source_dir / "file.txt").write_text("new-content")
    (target_dir / "file.txt").write_text("existing-content")

    result = copy_skill_dir(str(source_dir), str(target_dir), yes=True)

    assert result.status == "backed_up"
    assert result.backup_path is not None
    assert os.path.exists(result.backup_path)
    assert (target_dir / "file.txt").read_text() == "new-content"
