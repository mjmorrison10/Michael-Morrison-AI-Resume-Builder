#!/usr/bin/env python3
"""
assemble_dossier.py

Rebuilds MASTER_AI_DOSSIER.md from the modular files in:
  Michael Morrison AI Resume Builder/dossier/*.md

Usage:
  python3 assemble_dossier.py

This is useful after editing one of the modular files. It keeps the master
prompt file in sync with the modular source of truth.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
BUILDER_DIR = REPO_ROOT / "Michael Morrison AI Resume Builder"
DOSSIER_DIR = BUILDER_DIR / "dossier"
MASTER = BUILDER_DIR / "MASTER_AI_DOSSIER.md"

ORDER = [
    "rules.md",
    "identity.md",
    "timeline.md",
    "roles.md",
    "ventures.md",
    "sales_history.md",
]

HEADER = """# ============================================================
# MASTER AI DOSSIER - MICHAEL MORRISON
# Reusable "Context Prompt" for generating tailored resumes
# ============================================================
# HOW TO USE THIS FILE (read first):
# Paste this entire document into any AI, then add: "Using ONLY the facts
# in this dossier, write a resume tailored to [JOB TITLE / JOB DESCRIPTION]."
# The AI must follow the RULES OF ENGAGEMENT below. Do not invent facts.
# Last updated: 2026-07-06
# ============================================================
# NOTE: This file is assembled from the modular files in dossier/*.md.
# Edit the modular files, not this one, to keep the source of truth clean.
# ============================================================
"""


def main() -> int:
    missing = [f for f in ORDER if not (DOSSIER_DIR / f).exists()]
    if missing:
        print(f"Error: missing modular files: {missing}", file=sys.stderr)
        return 1

    parts = [HEADER]
    for filename in ORDER:
        content = (DOSSIER_DIR / filename).read_text(encoding="utf-8")
        parts.append(content)
        parts.append("")

    MASTER.write_text("\n".join(parts), encoding="utf-8")
    print(f"Assembled {MASTER}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
