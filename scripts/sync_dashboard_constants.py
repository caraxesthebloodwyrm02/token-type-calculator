#!/usr/bin/env python3
"""Emit dashboard_constants.generated.js from canonical_library.py.

Regenerate whenever TOKEN_WEIGHTS, TOKEN_COLORS, TOKEN_LABELS, ZONE_COLORS,
STRENGTH_MULTIPLIER, or SCENARIO_LIBRARY change:

    uv run python scripts/sync_dashboard_constants.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "dashboard_constants.generated.js"


def main() -> None:
    from canonical_library import (
        SCENARIO_LIBRARY,
        STRENGTH_MULTIPLIER,
        TOKEN_COLORS,
        TOKEN_LABELS,
        TOKEN_WEIGHTS,
        ZONE_COLORS,
    )

    scenarios_plain = {
        name: {
            "pressure": fp.pressure,
            "clarity": fp.clarity,
            "movement": fp.movement,
            "dominant_type": fp.dominant_type,
            "is_no_take": fp.is_no_take,
        }
        for name, fp in SCENARIO_LIBRARY.items()
    }

    banner = (
        "// AUTO-GENERATED — do not edit by hand.\n"
        "// Source: canonical_library.py (TOKEN_*, ZONE_COLORS, STRENGTH_MULTIPLIER, SCENARIO_LIBRARY)\n"
        "// Regenerate: uv run python scripts/sync_dashboard_constants.py\n\n"
    )

    def embed(obj: object) -> str:
        return f"JSON.parse({json.dumps(json.dumps(obj))})"

    body = (
        f"const TOKEN_COLORS = {embed(TOKEN_COLORS)};\n"
        f"const TOKEN_WEIGHTS = {embed(TOKEN_WEIGHTS)};\n"
        f"const TOKEN_LABELS = {embed(TOKEN_LABELS)};\n"
        f"const ZONE_COLORS = {embed(ZONE_COLORS)};\n"
        f"const STRENGTH_MULTIPLIER = {json.dumps(STRENGTH_MULTIPLIER)};\n"
        f"const SCENARIO_LIBRARY = {embed(scenarios_plain)};\n"
    )

    OUT.write_text(banner + body, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
