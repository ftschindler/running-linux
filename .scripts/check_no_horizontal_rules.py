#!/usr/bin/env python3
"""Check that markdown files don't contain horizontal rules (---)."""

import re
import sys
from pathlib import Path


def check_file(filepath: Path) -> list[str]:
    """Check a single file for horizontal rules.

    Returns list of error messages (empty if clean).
    """
    errors = []
    content = filepath.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Match horizontal rules: ---, ***, ___ (3 or more)
    # But not in code blocks or frontmatter
    in_code_block = False
    in_frontmatter = False

    for line_num, line in enumerate(lines, start=1):
        # Track code blocks
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        # Track frontmatter (between first --- pair)
        if line_num == 1 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter and line.strip() == "---":
            in_frontmatter = False
            continue

        # Skip if in code block or frontmatter
        if in_code_block or in_frontmatter:
            continue

        # Check for horizontal rule patterns
        if re.match(r"^(\s*---+\s*|\s*\*\*\*+\s*|\s*___+\s*)$", line):
            errors.append(
                f"{filepath}:{line_num}: Horizontal rule found. "
                "AI agents often overuse '---' as section dividers. "
                "Use headings (##, ###) or blank lines instead."
            )

    return errors


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: check_no_horizontal_rules.py <file> [file ...]")
        return 1

    all_errors = []
    for filepath_str in sys.argv[1:]:
        filepath = Path(filepath_str)
        if filepath.suffix.lower() == ".md":
            errors = check_file(filepath)
            all_errors.extend(errors)

    if all_errors:
        for error in all_errors:
            print(error)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
