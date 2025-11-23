# Exception Handling Audit

## Silent exception handling

- `openskills/operations.py` — `_read_skill_document` wraps `load_skill_document` in a broad `except Exception` and returns `None` when any error occurs.【F:openskills/operations.py†L29-L48】\
  When `_discover_skill_candidates` iterates over `SKILL.md` files, any parsing or file errors are therefore silently ignored and the skill is skipped without warning, leaving users with no feedback that a skill was rejected due to an error.【F:openskills/operations.py†L36-L48】

## Notes

No other exception handlers in the Python project fully suppress errors without emitting a message or warning.
