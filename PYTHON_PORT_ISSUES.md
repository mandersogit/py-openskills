# Python Port Issues Discovered

- **CLI commands are stubs**: All user-facing commands call `exit_not_implemented`, so the Python binary currently exits with code 99 instead of performing installs, listing, reading, syncing, managing, or removing skills.【F:openskills/cli.py†L17-L71】
- **Helper-only coverage**: Tests exercise help text and individual utilities, but there are no integration tests (or wiring) that combine Git fetch, validation, file transfer, and rendering into real workflows, leaving the port unusable end-to-end.【F:tests/python/test_cli.py†L15-L44】【F:tests/python/test_repo_service.py†L15-L52】【F:tests/python/test_fs_ops.py†L1-L77】
- **Skill discovery bypasses validation**: `discover_skills` pulls descriptions via a regex without verifying YAML frontmatter or required fields, so malformed or partial SKILL.md files could be reported as valid entries instead of being rejected or warned.【F:openskills/utils/skills.py†L27-L60】【F:openskills/utils/yaml.py†L11-L18】
