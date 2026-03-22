#!/usr/bin/env python3
"""Backward-compatible wrapper for repo-level symlink management."""

from __future__ import annotations

import runpy
from pathlib import Path


def main() -> int:
    script = Path(__file__).resolve().parents[3] / "scripts" / "apply_symlinks.py"
    runpy.run_path(str(script), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
