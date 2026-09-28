#!/usr/bin/env python3
"""Validate the Mesh per-Skill version and source-identity contract."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Iterable

SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
IGNORED_PARTS = {
    ".git",
    ".github",
    ".venv",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "generated",
    "vendor",
}
CONTROL_FILES = {"VERSION", "SKILL-METADATA.json"}
INFRA_ROOT_FILES = {
    "README.md",
    "CHANGELOG.md",
    "RELEASE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "AGENTS.md",
    "PORTABLE.md",
    "THIRD_PARTY_NOTICES.md",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "requirements.txt",
}


class ValidationError(RuntimeError):
    pass


def parse_semver(value: str) -> tuple[int, int, int, tuple[tuple[int, object], ...] | None]:
    match = SEMVER_RE.fullmatch(value)
    if not match:
        raise ValidationError(f"invalid SemVer: {value!r}")
    core = tuple(int(match.group(i)) for i in range(1, 4))
    prerelease = match.group(4)
    if prerelease is None:
        pre_key = None
    else:
        parts: list[tuple[int, object]] = []
        for item in prerelease.split("."):
            if item.isdigit():
                parts.append((0, int(item)))
            else:
                parts.append((1, item))
        pre_key = tuple(parts)
    return (*core, pre_key)


def semver_greater(current: str, previous: str) -> bool:
    c_major, c_minor, c_patch, c_pre = parse_semver(current)
    p_major, p_minor, p_patch, p_pre = parse_semver(previous)
    c_core = (c_major, c_minor, c_patch)
    p_core = (p_major, p_minor, p_patch)
    if c_core != p_core:
        return c_core > p_core
    if c_pre is None:
        return p_pre is not None
    if p_pre is None:
        return False
    return c_pre > p_pre


def run_git(args: list[str], root: Path, *, allow_failure: bool = False) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        if allow_failure:
            return None
        raise ValidationError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def parse_skill_name(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValidationError(f"{skill_md}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValidationError(f"{skill_md}: unclosed YAML frontmatter")
    header = text[4:end]
    match = re.search(r"""(?m)^name:\s*["']?([^"'\n]+?)["']?\s*$""", header)
    if not match:
        raise ValidationError(f"{skill_md}: missing frontmatter name")
    return match.group(1).strip()


def discover_skill_roots(root: Path) -> list[Path]:
    roots: list[Path] = []
    for skill_md in sorted(root.rglob("SKILL.md")):
        rel = skill_md.relative_to(root)
        if any(part in IGNORED_PARTS for part in rel.parts):
            continue
        if "tests" in rel.parts and "fixtures" in rel.parts:
            continue
        roots.append(skill_md.parent)
    return roots


def canonical_source_path(root: Path, skill_root: Path) -> str:
    rel = skill_root.resolve().relative_to(root.resolve())
    return "." if not rel.parts else PurePosixPath(*rel.parts).as_posix()


def load_version(skill_root: Path) -> str:
    path = skill_root / "VERSION"
    if not path.is_file():
        raise ValidationError(f"{skill_root}: missing VERSION")
    version = path.read_text(encoding="utf-8").strip()
    if "\n" in version or "\r" in version:
        raise ValidationError(f"{path}: VERSION must contain one line")
    parse_semver(version)
    return version


def load_metadata(skill_root: Path) -> dict[str, object]:
    path = skill_root / "SKILL-METADATA.json"
    if not path.is_file():
        raise ValidationError(f"{skill_root}: missing SKILL-METADATA.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"{path}: metadata must be a JSON object")
    return data


def validate_identity(
    repo_root: Path,
    skill_root: Path,
    repository: str | None,
) -> tuple[str, str]:
    name = parse_skill_name(skill_root / "SKILL.md")
    version = load_version(skill_root)
    metadata = load_metadata(skill_root)
    expected_path = canonical_source_path(repo_root, skill_root)

    expected = {
        "schema_version": 1,
        "name": name,
        "version": version,
        "source_path": expected_path,
    }
    for key, value in expected.items():
        if metadata.get(key) != value:
            raise ValidationError(
                f"{skill_root}: SKILL-METADATA.json {key}={metadata.get(key)!r}, expected {value!r}"
            )

    metadata_repo = metadata.get("source_repository")
    if not isinstance(metadata_repo, str) or not re.fullmatch(
        r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", metadata_repo
    ):
        raise ValidationError(f"{skill_root}: invalid source_repository")
    if repository and metadata_repo != repository:
        raise ValidationError(
            f"{skill_root}: source_repository={metadata_repo!r}, expected {repository!r}"
        )
    return name, version


def package_relevant(rel_to_skill: str) -> bool:
    path = PurePosixPath(rel_to_skill)
    if not path.parts:
        return False
    if any(part in IGNORED_PARTS for part in path.parts):
        return False
    if len(path.parts) == 1 and path.name in CONTROL_FILES | INFRA_ROOT_FILES:
        return False
    if path.as_posix() == "scripts/validate_skill_versions.py":
        return False
    if path.name.endswith(".pyc"):
        return False
    return True


def base_file(root: Path, base_ref: str, rel_path: str) -> str | None:
    return run_git(["show", f"{base_ref}:{rel_path}"], root, allow_failure=True)


def validate_version_bump(
    repo_root: Path,
    skill_root: Path,
    current_version: str,
    base_ref: str,
) -> None:
    skill_rel = canonical_source_path(repo_root, skill_root)
    version_rel = "VERSION" if skill_rel == "." else f"{skill_rel}/VERSION"
    previous_raw = base_file(repo_root, base_ref, version_rel)
    if previous_raw is None:
        return
    previous_version = previous_raw.strip()
    parse_semver(previous_version)

    diff = run_git(["diff", "--name-only", f"{base_ref}...HEAD"], repo_root) or ""
    changed = [line for line in diff.splitlines() if line.strip()]
    relevant: list[str] = []
    for changed_path in changed:
        if skill_rel == ".":
            rel = changed_path
        else:
            prefix = f"{skill_rel}/"
            if not changed_path.startswith(prefix):
                continue
            rel = changed_path[len(prefix):]
        if package_relevant(rel):
            relevant.append(changed_path)

    if current_version == previous_version and relevant:
        sample = ", ".join(relevant[:5])
        raise ValidationError(
            f"{skill_root}: package content changed without VERSION bump from "
            f"{previous_version}; changed: {sample}"
        )
    if current_version != previous_version and not semver_greater(current_version, previous_version):
        raise ValidationError(
            f"{skill_root}: VERSION must increase; base={previous_version}, current={current_version}"
        )


def validate_repository(
    root: Path,
    *,
    repository: str | None = None,
    base_ref: str | None = None,
) -> list[dict[str, str]]:
    skill_roots = discover_skill_roots(root)
    if not skill_roots:
        raise ValidationError("no deployable SKILL.md files found")
    report: list[dict[str, str]] = []
    for skill_root in skill_roots:
        name, version = validate_identity(root, skill_root, repository)
        if base_ref:
            validate_version_bump(root, skill_root, version, base_ref)
        report.append({
            "name": name,
            "version": version,
            "source_path": canonical_source_path(root, skill_root),
        })
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--base-ref")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.root).resolve()
    try:
        report = validate_repository(root, repository=args.repository, base_ref=args.base_ref)
    except (OSError, ValidationError) as exc:
        print(f"skill-version-validation: FAIL: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"skills": report}, sort_keys=True))
    else:
        for item in report:
            print(f"{item['name']} {item['version']} {item['source_path']}")
        print(f"skill-version-validation: PASS ({len(report)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
