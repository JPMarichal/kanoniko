#!/usr/bin/env python3
"""Validate backlog JSON files against their schemas + slug uniqueness.

Thin CLI wrapper over ``alejandria.backlogs.validate.main``. Intended
for use by the pre-commit hook and by developers debugging backlog
edits:

    python scripts/validate_backlogs.py               # validate all four
    python scripts/validate_backlogs.py discovery     # validate one
    python scripts/validate_backlogs.py --root path/to/backlogs

Exits 0 on clean validation, 1 on any error (messages go to stderr).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure src/ is on the path when invoked as scripts/validate_backlogs.py
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from alejandria.backlogs.validate import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
