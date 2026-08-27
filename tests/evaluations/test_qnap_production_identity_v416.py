from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def read(path: str) -> str: return (ROOT / path).read_text()

def test_v416_preserves_canonical_phase1_contract_and_catalog() -> None:
    contract = json.loads(read("chatgpt/mcp/mesh-cos-mcp.v1.json")); assert contract["runtime_release"] == "4.0.0"; assert len(contract["agent_tool_allowlists"]) == 10; assert len(contract["agent_tool_allowlists"]["cos"]) == 27; assert "message-ops" in contract["agent_tool_allowlists"]; assert "devils-advocate" not in contract["agent_tool_allowlists"]; assert set(contract["human_tool_allowlist"]) == {"approval.record_decision", "reliability.human_override"}; assert set(contract["human_tool_allowlist"]).isdisjoint(contract["agent_tool_allowlists"]["cos"])

def test_remote_runtime_requires_and_reports_deployment_identity() -> None:
    server = read("mcp/src/server.ts"); remote = read("mcp/src/remote.ts"); compose = read("deployment/qnap/compose.yaml"); assert "requireDeploymentRelease" in server; assert "deployment_release" in server; assert "requireDeploymentRelease(env)" in remote; assert "SECURE_MCP_TUNNEL" in remote; assert "version:deploymentRelease" in remote; assert "MESH_COS_DEPLOYMENT_RELEASE: ${MESH_COS_DEPLOYMENT_RELEASE:?deployment release required}" in compose

def test_active_release_train_is_v4117_and_ci_uses_setup_node_v7() -> None:
    dockerfile = read("Dockerfile"); env_example = read("deployment/qnap/.env.example"); prepare = read("deployment/qnap/scripts/mesh-cos-mcp-prepare.sh"); builder = read("scripts/build-qnap-release-bundle.sh"); ci = read(".github/workflows/ci.yml")
    assert "IMAGE_VERSION=4.1.17-qnap" in dockerfile; assert "MESH_COS_DEPLOYMENT_RELEASE=4.1.17" in env_example; assert "MESH_COS_DEPLOYMENT_RELEASE:-4.1.10" not in prepare; assert "mesh_candidate_release" in prepare; assert "VERSION=${1:-4.1.17}" in builder; assert 'RELEASE_DIR="$BUNDLE/v${VERSION}"' in builder; assert "actions/setup-node@v7" in ci; assert "actions/setup-node@v6" not in ci; assert "Build exact v4.1.17 QNAP release bundle" in ci; assert "mesh-cos-mcp-qnap-v4.1.17.zip" in ci

def test_historical_and_current_docs_are_packaged() -> None:
    builder = read("scripts/build-qnap-release-bundle.sh")
    for path in ["docs/security-review-v4.1.16.md", "docs/release-4.1.16-qnap-restarting-backup.md", "docs/verification-v4.1.16-qnap-restarting-backup.md", "docs/chatgpt-published-app-production-acceptance-v4.1.16.md", "specs/qnap-restarting-backup-v4.1.16.feature", "docs/security-review-v4.1.17.md", "docs/release-4.1.17-slack-bot-block-kit-hitl.md", "docs/verification-v4.1.17-slack-bot-block-kit-hitl.md", "docs/chatgpt-published-app-production-acceptance-v4.1.17.md", "specs/qnap-slack-thread-hitl-v4.1.17.feature"]:
        assert (ROOT / path).is_file(); assert Path(path).name in builder

def test_chatgpt_acceptance_requires_dedicated_bot_after_v4117_deploy() -> None:
    acceptance = read("deployment/qnap/CHATGPT-ACCEPTANCE.md")
    for token in ["v4.1.17", "mcp_version", "4.0.0", "deployment_release", "agent_id", "SECURE_MCP_TUNNEL", "27 agent-facing tools", "10 registered agents", "slack-adapter", "SLACK_BOT_API", "ChatGPT Enterprise AI Agent", "Approve", "Deny", "Change"]: assert token in acceptance
    assert "/mesh-approval" not in acceptance
