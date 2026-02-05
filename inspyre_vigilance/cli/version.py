from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from importlib import metadata

from packaging.version import InvalidVersion, Version


PACKAGE_NAME = "inspyre-vigilance"
PYPI_JSON_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
UPDATE_ENV_VAR = "MIDIFF_CHECK_UPDATES"


def get_installed_version() -> str:
    try:
        return metadata.version(PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return "unknown"


def fetch_latest_version() -> tuple[str | None, str | None]:
    try:
        with urllib.request.urlopen(PYPI_JSON_URL, timeout=5) as response:
            payload = json.load(response)
        return payload.get("info", {}).get("version"), None
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        return None, str(exc)


def compare_versions(installed: str, latest: str) -> int | None:
    try:
        installed_version = Version(installed)
        latest_version = Version(latest)
    except InvalidVersion:
        return None
    if installed_version < latest_version:
        return -1
    if installed_version > latest_version:
        return 1
    return 0


def print_version_info(check_updates: bool | None = None) -> int:
    installed = get_installed_version()
    print(f"Inspyre Vigilance version: {installed}")

    if check_updates is None:
        check_updates = bool(os.getenv(UPDATE_ENV_VAR))

    if not check_updates:
        return 0

    latest, error = fetch_latest_version()
    if error:
        print(f"Update check failed: {error}", file=sys.stderr)
        return 0
    if not latest:
        print("Update check failed: missing version data.", file=sys.stderr)
        return 0

    comparison = compare_versions(installed, latest)
    if comparison is None:
        print("Update check skipped: invalid version data.", file=sys.stderr)
        return 0
    if comparison < 0:
        print(f"Update available: {latest}")
    else:
        print("You are up to date.")
    return 0
