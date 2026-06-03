#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["packaging"]
# ///
"""Ensure .python-version is consistent with requires-python in pyproject.toml."""

import sys
import tomllib
from pathlib import Path

from packaging.specifiers import SpecifierSet
from packaging.version import Version

python_version_file = Path(".python-version")
pyproject_file = Path("pyproject.toml")

pinned = python_version_file.read_text().strip()
version = Version(pinned)

with pyproject_file.open("rb") as f:
    pyproject = tomllib.load(f)

requires_python = pyproject["project"]["requires-python"]
specifier = SpecifierSet(requires_python)

if version not in specifier:
    print(
        f"Mismatch: .python-version pins Python {pinned!r}, "
        f"but pyproject.toml requires-python is {requires_python!r}.\n"
        f"Please keep both files in sync — see the [project] table in pyproject.toml."
    )
    sys.exit(1)
