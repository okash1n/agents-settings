#!/usr/bin/env python3
"""Apply repo-managed symlinks declared in symlinks.json."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text())


def expand_path(path: str) -> Path:
    return Path(path).expanduser()


def same_target(left: Path, right: Path) -> bool:
    return left.resolve(strict=False) == right.resolve(strict=False)


def has_skill_md(path: Path) -> bool:
    return (path / "SKILL.md").exists() or (path / "skill.md").exists()


def remove_entry(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    shutil.rmtree(path)


def ensure_symlink(target: Path, source: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.is_symlink():
        if same_target(target, source):
            return
        target.unlink()
    elif target.exists():
        print(f"[skip] non-symlink target exists: {target}")
        return

    target.symlink_to(source)
    print(f"[link] {target} -> {source}")


def cleanup_managed_skill_links(agent_root: Path, shared_root: Path, managed: dict[str, Path]) -> None:
    if not agent_root.exists():
        return

    valid_names = set(managed)
    for candidate in agent_root.iterdir():
        if not candidate.is_symlink():
            continue
        target = candidate.resolve(strict=False)
        if shared_root not in target.parents and target != shared_root:
            continue
        if candidate.name not in valid_names:
            candidate.unlink(missing_ok=True)
            print(f"[cleanup] removed stale managed skill link: {candidate}")


def move_children(src_dir: Path, dst_dir: Path, managed_names: set[str]) -> None:
    for child in sorted(src_dir.iterdir(), key=lambda p: p.name):
        dst = dst_dir / child.name
        if dst.exists() or dst.is_symlink():
            if child.is_symlink() and dst.is_symlink() and same_target(child, dst):
                child.unlink()
                continue
            if child.name in managed_names:
                remove_entry(child)
                print(f"[remove] superseded managed entry: {child}")
                continue
            print(f"[skip] destination already exists: {dst}")
            continue
        shutil.move(str(child), str(dst))
        print(f"[move] {child} -> {dst}")


def replace_skills_dir_with_symlink(home_root: Path, repo_root: Path, managed_names: set[str]) -> None:
    home_root.parent.mkdir(parents=True, exist_ok=True)
    repo_root.mkdir(parents=True, exist_ok=True)

    if home_root.is_symlink():
        if same_target(home_root, repo_root):
            return
        current_target = home_root.resolve(strict=False)
        print(f"[skip] unexpected skills symlink: {home_root} -> {current_target}")
        return

    if home_root.exists():
        if not home_root.is_dir():
            print(f"[skip] non-directory skills target exists: {home_root}")
            return
        move_children(home_root, repo_root, managed_names)
        home_root.rmdir()
        print(f"[remove] {home_root}")

    home_root.symlink_to(repo_root)
    print(f"[link] {home_root} -> {repo_root}")


def build_shared_skill_map(manifest: dict, repo_root: Path) -> dict[str, dict[str, Path]]:
    per_agent: dict[str, dict[str, Path]] = {}
    for item in manifest["shared_skills"]:
        source = (repo_root / item["source"]).resolve()
        if not source.is_dir() or not has_skill_md(source):
            raise SystemExit(f"invalid shared skill source: {source}")
        for agent in item["agents"]:
            per_agent.setdefault(agent, {})[item["name"]] = source
    return per_agent


def apply_shared_skills(manifest: dict, repo_root: Path) -> dict[str, set[str]]:
    shared_root = (repo_root / "skills").resolve()
    per_agent = build_shared_skill_map(manifest, repo_root)
    managed_names: dict[str, set[str]] = {}

    for agent, mapping in sorted(per_agent.items()):
        agent_root = repo_root / agent / "skills"
        agent_root.mkdir(parents=True, exist_ok=True)
        for name, source in sorted(mapping.items()):
            ensure_symlink(agent_root / name, source)
        cleanup_managed_skill_links(agent_root, shared_root, mapping)
        managed_names[agent] = set(mapping)

    return managed_names


def apply_home_symlinks(manifest: dict, repo_root: Path, managed_skill_names: dict[str, set[str]]) -> None:
    for entry in manifest["home_symlinks"]:
        source = repo_root / entry["source"]
        target = expand_path(entry["target"])
        kind = entry["kind"]

        if kind == "file":
            ensure_symlink(target, source)
            continue

        if kind == "skills_dir":
            agent = entry["agent"]
            replace_skills_dir_with_symlink(target, source, managed_skill_names.get(agent, set()))
            continue

        raise SystemExit(f"unknown symlink kind: {kind}")


def main() -> int:
    repo_root = repo_root_from_script()
    manifest = load_manifest(repo_root / "symlinks.json")
    managed_skill_names = apply_shared_skills(manifest, repo_root)
    apply_home_symlinks(manifest, repo_root, managed_skill_names)
    print("[ok] symlinks applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
