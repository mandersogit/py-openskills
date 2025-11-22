"""File operations with overwrite safeguards for skill transfers."""

from __future__ import annotations

import os
import shutil
import time
from dataclasses import dataclass
from typing import Callable, Literal, Optional

PromptFn = Callable[[str], bool]


@dataclass
class TransferResult:
    status: Literal["copied", "backed_up", "moved", "skipped"]
    target_path: str
    backup_path: Optional[str] = None


def backup_skill_dir(target_dir: str, backup_root: Optional[str] = None) -> str:
    """Backup an existing skill directory before overwrite."""

    root = backup_root or os.path.dirname(target_dir)
    backup_path = os.path.join(root, f"{os.path.basename(target_dir)}.backup-{int(time.time() * 1000)}")

    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    shutil.copytree(target_dir, backup_path)
    return backup_path


def copy_skill_dir(
    source_dir: str,
    target_dir: str,
    *,
    yes: bool = False,
    prompt: Optional[PromptFn] = None,
    backup_root: Optional[str] = None,
) -> TransferResult:
    """Copy a skill directory with overwrite safeguards and optional backup."""

    target_exists = os.path.exists(target_dir)

    if target_exists:
        if not yes:
            should_overwrite = prompt(f"Skill already exists at {target_dir}. Overwrite?") if prompt else False
            if not should_overwrite:
                return TransferResult(status="skipped", target_path=target_dir)

        backup_path = backup_skill_dir(target_dir, backup_root)
        shutil.rmtree(target_dir)
        os.makedirs(os.path.dirname(target_dir), exist_ok=True)
        shutil.copytree(source_dir, target_dir)
        return TransferResult(status="backed_up", target_path=target_dir, backup_path=backup_path)

    os.makedirs(os.path.dirname(target_dir), exist_ok=True)
    shutil.copytree(source_dir, target_dir)
    return TransferResult(status="copied", target_path=target_dir)


def move_skill_dir(
    source_dir: str,
    target_dir: str,
    *,
    yes: bool = False,
    prompt: Optional[PromptFn] = None,
    backup_root: Optional[str] = None,
) -> TransferResult:
    """Move a skill directory with overwrite safeguards and optional backup."""

    result = copy_skill_dir(source_dir, target_dir, yes=yes, prompt=prompt, backup_root=backup_root)

    if result.status != "skipped":
        shutil.rmtree(source_dir)
        return TransferResult(status="moved", target_path=result.target_path, backup_path=result.backup_path)

    return result
