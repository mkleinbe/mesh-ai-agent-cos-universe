from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v4121_delegation_schema_requires_only_canonical_work_contract() -> None:
    schemas = json.loads(read("chatgpt/mcp/tool-input-schemas.v1.json"))
    assert schemas["tools"]["delegation.create"]["required"] == ["delegation"]
    for assertion in ("parent_authority", "depth", "ancestry", "active_owner"):
        assert assertion in schemas["tools"]["delegation.create"]["properties"]


def test_v4121_skill_documents_agent_vs_capability_and_parent_reconciliation() -> None:
    skill = read("chatgpt/skills/mesh-chief-of-staff/SKILL.md")
    assert "delegation.execute_owner" in skill
    assert "Never pass an agent identity through `skills.invoke_governed`" in skill
    assert "server-derived compatibility assertions" in skill
    assert "reconcile the returned result to the parent" in skill


def test_superseded_release_publishers_are_historical_read_only() -> None:
    for version in ("4.10.0", "4.11.0", "4.12.0"):
        workflow = read(f".github/workflows/release-v{version}.yml")
        assert "workflow_dispatch:" in workflow
        assert "pull_request:" not in workflow
        assert "push:" not in workflow
        assert "contents: write" not in workflow
        assert "gh release create" not in workflow


def test_v4121_release_assets_and_current_source_qnap_candidate_are_declared() -> None:
    workflow = read(".github/workflows/release-v4.12.1.yml")
    assert "gh release create v4.12.1" in workflow
    assert "mesh-cos-chief-of-staff-v4.12.1.zip" in workflow
    assert "mesh-cos-mcp-qnap-v4.4.0.zip" in workflow
    assert "tests/evaluations/test_cos_delegation_reporting_v4121.py" in workflow
    assert "tests/evaluations/test_release_closeout_v4121.py" in workflow
    builder = read("scripts/build-chatgpt-skill-bundle-v4.12.1.sh")
    assert "VERSION=4.12.1" in builder
    assert "docs/skills-v4.12.1.md" in builder
