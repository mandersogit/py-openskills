# Documentation Transformation Plan for Py-OpenSkills

This plan tracks the updates needed to align project documentation with the new Python-based direction for Py-OpenSkills.

## Scope

The following documents still reflect the legacy Node/TypeScript implementation and need revisions to match the Python port.

### CONTRIBUTING.md
- Replace TypeScript-specific coding standards with Python guidelines (typing, formatting, linting, testing).
- Update development setup to use `pip`, virtual environments, `pytest`, and relevant Python tooling instead of `npm` workflows.
- Refresh project structure diagrams to reflect the Python package layout.
- Align testing instructions with the Python test suite and coverage tools.

### SECURITY.md
- Update dependency and runtime assumptions to reference the Python package (remove Node-specific notes such as `commander`).
- Document security considerations for Python packaging and the use of system `git` via `subprocess`.
- Refresh contact and reporting guidance if communication channels change with the new project identity.

### README.md (follow-up validation)
- Confirm the new Python-focused introduction stays accurate as features ship and remove leftover references to the legacy Node CLI.
- Expand setup and usage once the Python entry points and commands stabilize.
- Update version references to reflect the new Python 3.11+ baseline and highlight the shift to modern typing conventions.

### PYTHON_PORT_PLAN.md (validation)
- Verify the roadmap aligns with current milestones and add any missing documentation tasks related to the port.

## Next Steps

- Prioritize updating `CONTRIBUTING.md` and `SECURITY.md` to unblock contributors using the Python toolchain.
- Revisit this plan after each documentation update to track remaining gaps until all documents consistently represent Py-OpenSkills.
