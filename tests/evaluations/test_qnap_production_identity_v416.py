from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text()


def test_v416_preserves_canonical_phase1_contract_and_catalog() -> None:
    contract = json.loads(read("chatgpt/mcp/mesh-cos-mcp.v1.json"))
    assert contract["runtime_release"] == "4.0.0"
    assert len(contract["agent_tool_allowlists"]) == 10
    assert len(contract["agent_tool_allowlists"]["cos"]) == 27
    assert "message-ops" in contract["agent_tool_allowlists"]
    assert "devils-advocate" not in contract["agent_tool_allowlists"]
    assert set(contract["human_tool_allowlist"]) == {
        "approval.record_decision",
        "reliability.human_override",
    }
    assert set(contract["human_tool_allowlist"]).isdisjoint(
        contract["agent_tool_allowlists"]["cos"]
    )


def test_remote_runtime_requires_and_reports_deployment_identity() -> None:
    server = read("mcp/src/server.ts")
    remote = read("mcp/src/remote.ts")
    compose = read("deployment/qnap/compose.yaml")
    assert "requireDeploymentRelease" in server
    assert "deployment_release" in server
    assert "requireDeploymentRelease(env)" in remote
    assert "SECURE_MCP_TUNNEL" in remote
    assert "version:deploymentRelease" in remote
    assert "version:'4.1.4'" not in remote
    assert (
        "MESH_COS_DEPLOYMENT_RELEASE: ${MESH_COS_DEPLOYMENT_RELEASE:?deployment release required}"
        in compose
    )


def test_active_release_train_is_v4112_and_ci_uses_setup_node_v7() -> None:
    dockerfile = read("Dockerfile")
    env_example = read("deployment/qnap/.env.example")
    prepare = read("deployment/qnap/scripts/mesh-cos-mcp-prepare.sh")
    builder = read("scripts/build-qnap-release-bundle.sh")
    ci = read(".github/workflows/ci.yml")
    release = read(".github/workflows/release-production-readiness.yml")

    assert "IMAGE_VERSION=4.1.12-qnap" in dockerfile
    assert "MESH_COS_DEPLOYMENT_RELEASE=4.1.12" in env_example
    assert "MESH_COS_DEPLOYMENT_RELEASE:-4.1.10" not in prepare
    assert "mesh_candidate_release" in prepare
    assert "VERSION=${1:-4.1.12}" in builder
    assert 'RELEASE_DIR="$BUNDLE/v${VERSION}"' in builder
    assert "actions/setup-node@v7" in ci
    assert "actions/setup-node@v6" not in ci
    assert "v4.1.12" in ci
    assert "TAG: v4.1.12" in release
    assert "v4.1.12 QNAP Release-Root Bootstrap" in release


def test_historical_and_v4112_current_docs_are_packaged() -> None:
    builder = read("scripts/build-qnap-release-bundle.sh")
    for path in [
        "docs/qnap-security-review-v4.1.6.md",
        "docs/chatgpt-published-app-production-acceptance-v4.1.6.md",
        "docs/release-4.1.6-secure-mcp-published-app-identity.md",
        "specs/qnap-published-chatgpt-app-v4.1.6.feature",
        "docs/qnap-security-review-v4.1.7.md",
        "docs/qnap-image-provenance-envelope-debugging-v4.1.7.md",
        "docs/release-4.1.7-qnap-image-provenance-envelope.md",
        "specs/qnap-image-provenance-envelope-v4.1.7.feature",
        "docs/qnap-security-review-v4.1.8.md",
        "docs/release-4.1.8-mcp-contract-acceptance.md",
        "docs/chatgpt-published-app-production-acceptance-v4.1.8.md",
        "specs/qnap-mcp-production-acceptance-v4.1.8.feature",
        "docs/qnap-security-review-v4.1.9.md",
        "docs/release-4.1.9-documentation-closeout.md",
        "docs/chatgpt-published-app-production-acceptance-v4.1.9.md",
        "specs/qnap-release-closeout-v4.1.9.feature",
        "docs/qnap-security-review-v4.1.10.md",
        "docs/release-4.1.10-scheduled-slack-hitl.md",
        "docs/chatgpt-published-app-production-acceptance-v4.1.10.md",
        "specs/scheduled-automation-slack-hitl-v4.1.10.feature",
        "docs/qnap-security-review-v4.1.11.md",
        "docs/qnap-versioned-release-staging-v4.1.11.md",
        "docs/release-4.1.11-qnap-versioned-release-staging.md",
        "docs/verification-v4.1.11-qnap-versioned-release-staging.md",
        "docs/chatgpt-published-app-production-acceptance-v4.1.11.md",
        "specs/qnap-versioned-release-staging-v4.1.11.feature",
        "docs/qnap-security-review-v4.1.12.md",
        "docs/qnap-release-root-bootstrap-v4.1.12.md",
        "docs/release-4.1.12-qnap-release-root-bootstrap.md",
        "docs/verification-v4.1.12-qnap-release-root-bootstrap.md",
        "docs/chatgpt-published-app-production-acceptance-v4.1.12.md",
        "specs/qnap-release-root-bootstrap-v4.1.12.feature",
    ]:
        assert (ROOT / path).is_file()
        assert Path(path).name in builder


def test_chatgpt_acceptance_requires_dual_identity_after_v4112_deploy() -> None:
    acceptance = read("deployment/qnap/CHATGPT-ACCEPTANCE.md")
    for token in [
        "v4.1.12",
        "mcp_version",
        "4.0.0",
        "deployment_release",
        "agent_id",
        "SECURE_MCP_TUNNEL",
        "27 agent-facing tools",
        "exactly 10 agents",
        "validation_failed",
        "CHATGPT_SKILL_HANDOFF",
        "slack-adapter",
    ]:
        assert token in acceptance
