#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path


IGNORE_NAMES = shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc", "*.pyo")


def find_source_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def discover_source_skills(repo_root: Path) -> list[Path]:
    skills = []
    for child in sorted(repo_root.iterdir(), key=lambda path: path.name):
        if child.name.startswith(".") or not child.is_dir():
            continue
        if (child / "SKILL.md").is_file():
            skills.append(child)
    return skills


def parse_destination(raw_path: str, source_repo_root: Path) -> Path:
    expanded = Path(raw_path).expanduser()
    if not expanded.is_absolute():
        raise ValueError("destination path must be absolute")

    destination = expanded.resolve()
    if not destination.exists():
        raise ValueError(f"destination does not exist: {destination}")
    if not destination.is_dir():
        raise ValueError(f"destination is not a directory: {destination}")
    if destination == source_repo_root:
        raise ValueError("destination cannot be the source repository root")
    return destination


def stage_copy(source_skill: Path, destination_root: Path) -> Path:
    stage_root = Path(tempfile.mkdtemp(prefix=f".{source_skill.name}-sync-", dir=destination_root))
    staged_skill = stage_root / source_skill.name
    shutil.copytree(source_skill, staged_skill, ignore=IGNORE_NAMES)
    return staged_skill


def replace_skill(source_skill: Path, destination_root: Path) -> str:
    target_skill = destination_root / source_skill.name
    action = "update" if target_skill.exists() else "create"

    if target_skill.exists() and not target_skill.is_dir():
        raise RuntimeError(f"destination path exists but is not a directory: {target_skill}")

    staged_skill = stage_copy(source_skill, destination_root)
    stage_root = staged_skill.parent
    backup_skill = None

    try:
        if target_skill.exists():
            backup_skill = destination_root / f".{source_skill.name}.backup-{uuid.uuid4().hex}"
            os.replace(target_skill, backup_skill)
        os.replace(staged_skill, target_skill)
        if backup_skill is not None and backup_skill.exists():
            shutil.rmtree(backup_skill)
    except Exception:
        if backup_skill is not None and backup_skill.exists() and not target_skill.exists():
            os.replace(backup_skill, target_skill)
        raise
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)

    return action


def build_plan(source_skills: list[Path], destination_root: Path) -> list[tuple[Path, str]]:
    plan = []
    for source_skill in source_skills:
        action = "update" if (destination_root / source_skill.name).exists() else "create"
        plan.append((source_skill, action))
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync the top-level skills from this repository into another skills directory.",
    )
    parser.add_argument("destination", help="Absolute path to the destination skills directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview planned creates and updates without changing files",
    )
    args = parser.parse_args()

    source_repo_root = find_source_repo_root()
    try:
        destination_root = parse_destination(args.destination, source_repo_root)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    source_skills = discover_source_skills(source_repo_root)
    if not source_skills:
        print(f"[ERROR] no source skills found in {source_repo_root}", file=sys.stderr)
        return 1

    plan = build_plan(source_skills, destination_root)

    print(f"source repo: {source_repo_root}")
    print(f"destination: {destination_root}")

    if args.dry_run:
        for source_skill, action in plan:
            print(f"[DRY RUN] {action} {source_skill.name}")
        print(f"planned {len(plan)} skill syncs")
        return 0

    completed = 0
    for source_skill, _ in plan:
        action = replace_skill(source_skill, destination_root)
        completed += 1
        print(f"[OK] {action} {source_skill.name}")

    print(f"synced {completed} skill(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
