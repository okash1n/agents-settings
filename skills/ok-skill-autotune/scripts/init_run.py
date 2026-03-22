#!/usr/bin/env python3
"""Initialize a minimal autotune run directory for a target skill."""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path


def resolve_skill_md(path_text: str) -> Path:
    path = Path(path_text).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"SKILL.md not found: {path}")
    if path.name not in {"SKILL.md", "skill.md"}:
        raise ValueError(f"expected SKILL.md or skill.md, got: {path.name}")
    return path


def default_run_name(skill_md: Path) -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"autotune-{skill_md.parent.name}-{timestamp}"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_if_missing(path: Path, content: str) -> None:
    ensure_parent(path)
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True, help="Absolute path to target SKILL.md")
    parser.add_argument("--run-name", help="Optional run directory name")
    args = parser.parse_args()

    skill_md = resolve_skill_md(args.skill)
    run_name = args.run_name.strip() if args.run_name else default_run_name(skill_md)
    run_dir = skill_md.parent / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    baseline = run_dir / "SKILL.md.baseline"
    if not baseline.exists():
        shutil.copy2(skill_md, baseline)

    write_if_missing(
        run_dir / "results.tsv",
        "experiment\tscore\tmax_score\tpass_rate\tstatus\tchange_summary\n",
    )
    write_if_missing(
        run_dir / "changelog.md",
        "# Changelog\n\n",
    )
    write_if_missing(
        run_dir / "evals.md",
        "# Evals\n\n"
        "## User Complaints\n\n"
        "- [TODO: what felt bad in the current skill]\n\n"
        "## Desired Behavior\n\n"
        "- [TODO: what should become true after improvement]\n\n"
        "## Execution Harness\n\n"
        "- Agent: [TODO]\n"
        "- Invocation: [TODO]\n"
        "- Output location: [TODO]\n\n"
        "## Test Inputs\n\n"
        "- [TODO]\n\n"
        "## Binary Evals\n\n"
        "### EVAL 1: [TODO]\n"
        "- Complaint addressed: [TODO]\n"
        "- Question: [TODO]\n"
        "- Pass condition: [TODO]\n"
        "- Fail condition: [TODO]\n",
    )

    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
