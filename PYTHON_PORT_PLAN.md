# Python Port Plan for the OpenSkills CLI

This document captures the concrete plan to port the existing JavaScript/TypeScript CLI to Python using the [`click`](https://click.palletsprojects.com/) framework.

## Objectives
- Replicate the current CLI surface (commands, options, exit codes, help text) with Python parity.
- Preserve behavior for skill installation, listing/reading, AGENTS.md synchronization, and management/removal flows.
- Package the tool for easy installation and cross-platform use on Python 3.11+.

## Workstreams for Parallel Delivery
The work is partitioned into non-overlapping tracks so multiple contributors can proceed simultaneously with minimal merge conflicts.

1) **CLI Skeleton & Command Wiring (Click)**
   - Create the entry point module and `click` command group mirroring `legacy-typescript/src/cli.ts` (commands: `install`, `list`, `read`, `sync`, `manage`, `remove`).
   - Implement option/flag parity (aliases, defaults, `--help`, `--version`) and shared error/exit-code handling utilities.
   - Provide a stub implementation for each command that delegates to yet-to-be-built services; keep the file small to avoid conflicts.
   - Add initial parity tests that only assert CLI shape/help text to unblock other tracks.

2) **Git & Skill Fetching Service**
   - Build a pure-Python service that shells out to the system `git` executable for clone/fetch/pull.
   - Support owner/repo shorthand, HTTPS/SSH URLs, and local paths; include transparent temp directory handling for discovery before install.
   - Expose a function that produces a normalized skill folder ready for validation; keep interfaces stable for other teams.

3) **Skill Validation & Metadata Parsing**
   - Implement detection of valid skill directories, ensuring `SKILL.md` exists with YAML frontmatter.
   - Use `PyYAML` to parse metadata; supply structured models (dataclasses) consumed by list/read/sync flows.
   - Add strict/lenient modes to mirror current behavior (warnings vs hard failures) and unit tests with fixtures.

4) **Installation Flow & Path Layout**
   - Recreate target resolution for project-local, global (`.claude/skills`), and universal (`.agent/skills`) installs.
   - Support interactive selection (when available) vs `--yes` non-interactive installs; handle overwrite/merge safeguards.
   - Encapsulate file operations (copy/move, backups) in a module isolated from CLI wiring.

5) **List/Read/Sync Rendering**
   - Implement skill discovery across target locations and render outputs matching the Node tool (usage snippets, `<available_skills>` XML, descriptions, and paths).
   - Recreate AGENTS.md synchronization between `<!-- SKILLS_TABLE_START -->` and `<!-- SKILLS_TABLE_END -->`, with deterministic formatting for testability.
   - Provide fixtures and golden-file tests to guard against regressions.

6) **Manage/Remove Flows**
   - Implement interactive prompts (when optional dependencies are present) and non-interactive fallbacks for confirmations and multi-select removal.
   - Preserve messaging and exit statuses to maintain compatibility with existing automation.

7) **Packaging, Distribution, and Documentation**
   - Package as a Python module with a console entry point (e.g., `openskills`) and set the baseline to Python 3.11+.
   - Write installation/migration notes so Python and Node CLIs are interchangeable; document optional-dependency behavior and fallbacks.
   - Adopt Python 3.11-era typing (native generics, `Path.is_relative_to`) throughout new modules and ensure CI validates on 3.11+.

## Coordination Notes
- Keep command wiring minimal and delegate logic to services to avoid cross-branch churn.
- Use shared interfaces for Git fetch, skill models, and file layout so downstream work can start before all services are finished.
- Prefer additive tests and fixtures per workstream to minimize conflicts in shared test files.

## Non-Standard Library Dependencies
Aim to minimize runtime dependencies while matching current functionality:
- **Required**: `click` (CLI), `PyYAML` (YAML frontmatter).
- **Optional**: `questionary` (prompts/multi-select), `rich` (formatted console output), `packaging` (version/specifier helpers if needed).
- **Not Planned**: `GitPython`—all Git operations shell out to the system `git` via `subprocess`.

## Current Status
- **Command flows implemented**: All CLI commands delegate to full Python implementations for install, list, read, sync, manage, and remove, reusing the shared services for discovery, copying, working-copy prep, and AGENTS.md updates.【F:openskills/cli.py†L6-L71】【F:openskills/operations.py†L1-L246】
- **Core utilities landed**: Directory resolution, YAML/frontmatter parsing, skill discovery, and AGENTS.md rendering helpers have been implemented with accompanying unit tests to mirror the Node behavior for supporting services.【F:openskills/utils/dirs.py†L6-L77】【F:openskills/utils/yaml.py†L7-L23】【F:openskills/utils/skills.py†L11-L68】【F:openskills/utils/agents_md.py†L1-L76】【F:tests/python/test_dirs.py†L1-L51】【F:tests/python/test_renderers.py†L1-L78】
- **Repository handling established**: Git-backed working-copy preparation (shorthand normalization, local/remote support, commit capture, and cleanup) is available and validated via tests; fetch/pull helpers are in place for future flows.【F:openskills/utils/repo_service.py†L1-L82】【F:tests/python/test_repo_service.py†L1-L52】
- **File operations and validation**: Backups/moves/copies include overwrite prompts/flags, while `SKILL.md` validation covers frontmatter parsing and structured metadata with strict/lenient modes and tests.【F:openskills/utils/fs_ops.py†L1-L63】【F:openskills/utils/skill_validation.py†L1-L58】【F:tests/python/test_fs_ops.py†L1-L77】【F:tests/python/test_skill_validation.py†L1-L96】
- **Integration coverage**: Workflow tests exercise git-based installs, listing, reading, AGENTS.md sync, and removal flows using temporary repositories and mocked prompts.【F:tests/python/test_workflows.py†L1-L81】【F:tests/python/test_workflows.py†L82-L121】

## Next Steps
- **Packaging & distribution**: Publish the Python package with a console script entry point, define dependencies/optional extras, and verify installation on supported Python versions.
- **Documentation & migration**: Update README/SECURITY to explain Python usage, installation paths (project/global/universal), and parity notes for users migrating from the Node CLI.
- **Live git validation**: Add tests or manual checks against real remote git sources (not just local temp repos) to confirm networked workflows and error messaging.
