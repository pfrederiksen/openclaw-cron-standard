#!/usr/bin/env python3
"""Validate the OpenClaw cron standard skill repository."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SKILL_TERMS = (
    "ALREADY_CLAIMED",
    "NO_REPLY",
    "result JSON",
    "stale",
    "claim",
    "jobs-state.json",
    "job.state",
    'delivery.mode: "announce"',
    'delivery.mode: "none"',
    "reply-text delivery",
    "message",
)
REQUIRED_README_TERMS = (
    "jobs-state.json",
    "job.state",
    'delivery.mode: "announce"',
    'delivery.mode: "none"',
    "reply-text delivery",
)


def main() -> int:
    errors: list[str] = []
    skill_path = ROOT / "SKILL.md"
    readme_path = ROOT / "README.md"
    manifest_path = ROOT / "skill.toml"

    if not skill_path.exists():
        errors.append("SKILL.md is missing")
    else:
        skill_text = skill_path.read_text(encoding="utf-8")
        missing_terms = [term for term in REQUIRED_SKILL_TERMS if term not in skill_text]
        if missing_terms:
            errors.append(f"SKILL.md is missing required terms: {', '.join(missing_terms)}")
        if not re.search(r"^---\n.*?\n---", skill_text, flags=re.DOTALL):
            errors.append("SKILL.md is missing YAML front matter")

    if not readme_path.exists():
        errors.append("README.md is missing")
    else:
        readme_text = readme_path.read_text(encoding="utf-8")
        missing_terms = [term for term in REQUIRED_README_TERMS if term not in readme_text]
        if missing_terms:
            errors.append(f"README.md is missing required terms: {', '.join(missing_terms)}")

    if not manifest_path.exists():
        errors.append("skill.toml is missing")
    else:
        manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("skill", {}).get("name") != "openclaw-cron-standard":
            errors.append("skill.toml has the wrong skill name")
        if manifest.get("skill", {}).get("license") != "MIT":
            errors.append("skill.toml must declare MIT license")

    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
