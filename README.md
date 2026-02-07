# Inspyre‑Vigilance

Real-time system intelligence and event correlation framework.

## Running

Install dependencies and launch the default power detector to stdout:

```bash
pip install -e .
python -m inspyre_vigilance
```

## Versioning & Changelog

- The source of truth for the version is `[project].version` in `pyproject.toml`.
- For user-facing changes, update `CHANGELOG.md` under **[Unreleased]**.
- Use patch bumps for fixes, minor for features, and major for breaking changes.
- Pre-releases should use a PEP 440 dev suffix (for example, `0.3.0.dev1`).

## Release Workflow

See [.github/workflows/README.md](.github/workflows/README.md) for release triggers,
pre-release detection, required secrets, and publishing behavior.
