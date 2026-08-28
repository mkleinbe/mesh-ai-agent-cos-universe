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
    assert len(contract["agent_tool_allowlists"]["cos"]) == 28
    assert "delegation.execute_owner" in contract["agent_tool_allowlists"]["cos"]
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
    assert "source_commit" in server
    assert "publication_schema_digest" in server
    assert "requireDeploymentRelease(env)" in remote
    assert "SECURE_MCP_TUNNEL" in remote
    assert "version:deploymentRelease" in remote
    assert (
        "MESH_COS_DEPLOYMENT_RELEASE: ${MESH_COS_DEPLOYMENT_RELEASE:?deployment release required}"
        in compose
    )


def test_active_deployment_train_remains_v430_while_ci_is_release_neutral() -> None:
    env_example = read("deployment/qnap/.env.example")
    prepare = read("deployment/qnap/scripts/mesh-cos-mcp-prepare.sh")
    builder = read("scripts/build-qnap-release-bundle.sh")
    wrapper = read("scripts/build-qnap-release-v4.3.0.sh")
    ci = read(".github/workflows/ci.yml")
    assert "MESH_COS_DEPLOYMENT_RELEASE=4.3.0" in env_example
    assert "MESH_COS_SLACK_HITL_MODE=CHATGPT_NATIVE_EVENT_TRIGGER" in env_example
    assert "MESH_COS_SLACK_APP_ID=A0B49RNE4K0" in env_example
    assert "MESH_COS_DEPLOYMENT_RELEASE:-4.1.10" not in prepare
    assert "mesh_candidate_release" in prepare
    assert 'RELEASE_DIR="$BUNDLE/v${VERSION}"' in builder
    assert "VERSION=4.3.0" in wrapper
    assert "actions/setup-node@v7" in ci
    assert "actions/setup-node@v6" not in ci
    assert "Build exact v4.3.0 QNAP release bundle" not in ci
    assert "Build current-source QNAP CI candidate" in ci
    assert 'CANDIDATE_VERSION: \'4.4.0\'' in ci
    assert 'bash scripts/build-qnap-release-bundle.sh "$CANDIDATE_VERSION"' in ci
    assert "dist/mesh-cos-mcp-qnap-v4.4.0.zip" in ci
    assert "workspace_publication_status=BLOCKED_PENDING_ACTUAL_ACTION_SCHEMA_SNAPSHOT" in ci


def test_historical_and_current_docs_are_packaged() -> None:
    builder = read("scripts/build-qnap-release-bundle.sh")
    wrapper = read("scripts/build-qnap-release-v4.3.0.sh")
    for path in [
        "docs/security-review-v4.1.16.md",
        "docs/release-4.1.16-qnap-restarting-backup.md",
        "docs/verification-v4.1.16-qnap-restarting-backup.md",
        "docs/chatgpt-published-app-production-acceptance-v4.1.16.md",
        "specs/qnap-restarting-backup-v4.1.16.feature",
        "docs/security-review-v4.1.17.md",
        "docs/release-4.1.17-slack-bot-block-kit-hitl.md",
        "docs/verification-v4.1.17-slack-bot-block-kit-hitl.md",
        "docs/chatgpt-published-app-production-acceptance-v4.1.17.md",
        "specs/qnap-slack-thread-hitl-v4.1.17.feature",
    ]:
        assert (ROOT / path).is_file()
        assert Path(path).name in builder
    for path in [
        "CHANGELOG-v4.3.0.md",
        "docs/pf-057-cross-agent-owner-execution.md",
        "docs/security-review-v4.3.0-cross-agent-owner-execution.md",
        "docs/release-4.3.0-cross-agent-owner-execution.md",
        "docs/verification-v4.3.0-cross-agent-owner-execution.md",
        "docs/chatgpt-published-app-production-acceptance-v4.3.0.md",
        "specs/cross-agent-owner-execution.feature",
        "docs/chatgpt-native-slack-dispatcher-v4.2.3.md",
    ]:
        assert (ROOT / path).is_file()
        assert Path(path).name in wrapper


def test_chatgpt_acceptance_requires_owner_execution_after_v430_deploy() -> None:
    acceptance = read("deployment/qnap/CHATGPT-ACCEPTANCE.md")
    for token in [
        "v4.3.0",
        "mcp_version",
        "4.0.0",
        "deployment_release",
        "agent_id",
        "SECURE_MCP_TUNNEL",
        "28",
        "10",
        "delegation.execute_owner",
        "slack-adapter",
        "SLACK_BOT_API",
        "ChatGPT Enterprise AI Agent",
        "*APPROVE*",
        "DENY",
        "CHANGE",
        "CHATGPT_NATIVE_EVENT_TRIGGER",
        "conversations.replies",
        "A0B49RNE4K0",
        "qnet",
    ]:
        assert token in acceptance
    assert "/mesh-approval" not in acceptance
    assert "xapp-" in acceptance
    assert "not required or mounted" in acceptance
