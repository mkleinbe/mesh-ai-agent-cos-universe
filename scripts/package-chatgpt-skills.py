#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "chatgpt" / "skills"
INDEX = SKILLS_ROOT / "versions.json"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def source_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist/chatgpt-skills")
    parser.add_argument("--skill", action="append", default=[])
    args = parser.parse_args()

    index = json.loads(INDEX.read_text())
    if index.get("schema_version") != "mesh.skill-version-index.v1":
        raise SystemExit("unsupported skill version index")
    records = index.get("skills", {})
    selected = args.skill or sorted(records)
    unknown = sorted(set(selected) - set(records))
    if unknown:
        raise SystemExit(f"unknown skills: {unknown}")

    out = ROOT / args.output
    out.mkdir(parents=True, exist_ok=True)
    source = source_commit()
    artifacts = []

    for skill in selected:
        record = records[skill]
        skill_dir = ROOT / record["path"]
        version = (skill_dir / "VERSION").read_text().strip()
        if not SEMVER.fullmatch(version):
            raise SystemExit(f"{skill}: invalid SemVer {version!r}")
        if version != record.get("version"):
            raise SystemExit(f"{skill}: VERSION differs from versions.json")

        zip_path = out / f"{skill}-v{version}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(skill_dir.rglob("*")):
                if not path.is_file() or "__pycache__" in path.parts:
                    continue
                rel = Path(skill) / path.relative_to(skill_dir)
                info = zipfile.ZipInfo(rel.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o644 & 0xFFFF) << 16
                archive.writestr(info, path.read_bytes())

        with zipfile.ZipFile(zip_path) as archive:
            packaged_version = archive.read(f"{skill}/VERSION").decode().strip()
            if packaged_version != version:
                raise SystemExit(f"{skill}: packaged VERSION mismatch")

        artifacts.append({
            "skill": skill,
            "version": version,
            "source_commit": source,
            "asset": zip_path.name,
            "bytes": zip_path.stat().st_size,
            "sha256": sha256(zip_path),
        })

    manifest = {
        "schema_version": "mesh.chatgpt-skill-distribution.v1",
        "source_repository": "mkleinbe/mesh-ai-agent-cos-universe",
        "source_commit": source,
        "artifacts": artifacts,
    }
    (out / "distribution-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    with (out / "SHA256SUMS.txt").open("w") as handle:
        for item in artifacts:
            handle.write(f"{item['sha256']}  {item['asset']}\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
