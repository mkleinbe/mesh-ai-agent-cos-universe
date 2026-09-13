#!/usr/bin/env python3
"""Apply the v4.9.1 Mesh Media OS capability registration without changing authority."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "agents" / "registry.json"

EXPECTED = {
    "cmo": ["mesh-media-production", "mesh-media-verification", "mesh-media-distribution"],
    "vp-content": ["mesh-media-production"],
}


def main() -> int:
    payload = json.loads(REGISTRY.read_text())
    records = {record["agent_id"]: record for record in payload["agents"]}

    for agent_id, skills in EXPECTED.items():
        record = records[agent_id]
        existing = list(record.get("skills", []))
        for skill in skills:
            if skill not in existing:
                existing.append(skill)
        record["skills"] = existing

    cmo = records["cmo"]
    vp = records["vp-content"]
    if cmo.get("decision_authority") is None or vp.get("decision_authority") is None:
        raise SystemExit("authority metadata unexpectedly missing")
    if "vp-content" not in cmo.get("delegation_permissions", []):
        raise SystemExit("CMO direct-child delegation contract changed unexpectedly")
    if vp.get("delegation_permissions", []) != []:
        raise SystemExit("VP Content must retain zero delegation authority")

    for agent_id, required in EXPECTED.items():
        skills = records[agent_id].get("skills", [])
        missing = [skill for skill in required if skill not in skills]
        if missing:
            raise SystemExit(f"{agent_id} missing required media skills: {missing}")

    REGISTRY.write_text(json.dumps(payload, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
