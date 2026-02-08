# Release Workflow

This repository mirrors the MIDIDiff release workflow behavior.

## Trigger
- Runs on pushes to the default branch **only when** `pyproject.toml` changes.

## Version checks
- The workflow reads `[project].version` from `pyproject.toml`.
- If the version did **not** change compared to the previous commit, the workflow exits without releasing.

## Pre-release detection
- Uses a PEP 440-compatible regex to detect pre-release versions (`a`, `b`, `rc`, `alpha`, `beta`, `dev`).
- Pre-releases are published to **Test PyPI**.
- Stable releases are published to **PyPI**.

## Secrets
The workflow requires:
- `PYPI_TOKEN` for stable releases.
- `TEST_PYPI_TOKEN` for pre-releases.

## How to release
1. Update `[project].version` in `pyproject.toml`.
2. Update `CHANGELOG.md` under the **[Unreleased]** section with user-facing changes.
3. Merge or push the change to the default branch.
4. The workflow builds with Poetry, creates a GitHub Release, and uploads `dist/*` artifacts.

## CI Workflow

- Runs on pushes and pull requests across Ubuntu, macOS, and Windows runners.
- Installs Poetry (pinned to a stable version), installs the project with `poetry install --with dev`, and executes tests with `poetry run pytest` inside the Poetry environment.
- Caches Poetry artifacts keyed to `poetry.lock` to speed up installs across runs.
