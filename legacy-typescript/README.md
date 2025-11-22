# Legacy TypeScript Sources

This directory keeps the original Node/TypeScript implementation of the OpenSkills CLI intact while the Python port in the repository root continues. Package metadata, build configs, and Vitest suites were moved here without modification so the reference implementation stays available without cluttering the Python-focused layout.

To work with the TypeScript version, change into this directory and use the existing npm scripts (e.g., `npm install`, `npm run build`, `npm test`) against the preserved `src/` and `tests/` trees.
