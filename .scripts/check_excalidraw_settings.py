#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""Ensure Obsidian Excalidraw plugin settings produce portable .excalidraw files.

The plugin must save drawings as standard .excalidraw JSON (not .excalidraw.md)
so that mkdocs-excalidraw can render them. This requires:

- compatibilityMode: true   (saves as .excalidraw, not .excalidraw.md)
- compress: false            (plain JSON, not compressed markdown wrapper)
- autoexportSVG: false       (rendering handled client-side)
- autoexportPNG: false       (no pre-rendered exports to keep in sync)
"""

import json
import sys
from pathlib import Path

SETTINGS_PATH = Path(".obsidian/plugins/obsidian-excalidraw-plugin/data.json")

REQUIRED = {
    "compatibilityMode": True,
    "compress": False,
    "autoexportSVG": False,
    "autoexportPNG": False,
    "embedWikiLink": False,
}

if not SETTINGS_PATH.exists():
    # Plugin not installed — nothing to enforce.
    sys.exit(0)

settings = json.loads(SETTINGS_PATH.read_text())

errors = []
for key, expected in REQUIRED.items():
    actual = settings.get(key)
    if actual != expected:
        errors.append(f"  {key}: expected {expected!r}, got {actual!r}")

if errors:
    print(
        "Excalidraw plugin settings are incompatible with mkdocs-excalidraw:\n"
        + "\n".join(errors)
        + f"\n\nFix in {SETTINGS_PATH} or via the plugin's Settings > Saving tab."
    )
    sys.exit(1)
