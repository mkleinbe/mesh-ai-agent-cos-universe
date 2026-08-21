from __future__ import annotations

import json
from pathlib import Path

from mesh_cos import __version__

ROOT = Path(__file__).resolve().parents[2]
MCP_CONTRACT = ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json"
MANIFESTS = ROOT / "chatgpt" / "workspace-agents"
MCP_DIR = ROOT / "mcp"
RELEASE = "2.0.0"


def test_release_moves_to_v2_0_0_for_shared_mesh_devils_advocate() -> None:
    assert __version__ == RELEASE
    assert f'version = "{RELEASE}"' in (ROOT / "pyproject.toml").read_text()


def test_mcp_contract_makes_bundled_stdio_primary_and_remote_optional() -> None:
    contract = json.loads(MCP_CONTRACT.read_text())
    assert contract["runtime_release"] == RELEASE
    assert contract["transport"] == "LOCAL_STDIO"
    assert contract["local_runtime"]["command"] == "node"
    assert contract["local_runtime"]["args"] == ["mcp/dist/index.js"]
    assert contract["local_runtime"]["agent_identity_env"] == "MESH_COS_AGENT_ID"
    assert contract["local_runtime"]["ledger_path_env"] == "MESH_COS_LEDGER_PATH"
    assert "server_url_env" not in contract
    assert contract["deployment"]["chatgpt_runtime"] == "BUNDLED_LOCAL_STDIO"
    assert contract["deployment"]["managed_remote"] == "OPTIONAL_NOT_REQUIRED"
    assert len(contract["agent_tool_allowlists"]) == 10
    assert "devils-advocate" not in contract["agent_tool_allowlists"]


def test_all_workspace_agents_use_local_stdio_without_remote_url_dependency() -> None:
    manifests = sorted(MANIFESTS.glob("*.json"))
    assert len(manifests) == 10
    assert not (MANIFESTS / "devils-advocate.json").exists()
    for path in manifests:
        manifest = json.loads(path.read_text())
        assert manifest["repository_release"] == RELEASE, path.name
        mcp = manifest["mcp"]
        assert mcp["transport"] == "LOCAL_STDIO", path.name
        assert mcp["command"] == "node", path.name
        assert mcp["args"] == ["mcp/dist/index.js"], path.name
        assert mcp["env"]["MESH_COS_AGENT_ID"] == manifest["agent_id"], path.name
        assert mcp["env"]["MESH_COS_LEDGER_PATH"], path.name
        assert "server_url_env" not in mcp, path.name
        builder = manifest["builder_configuration"]
        assert builder["mcp_transport"] == "LOCAL_STDIO", path.name
        assert builder["mcp_command"] == "node", path.name
        assert builder["mcp_args"] == ["mcp/dist/index.js"], path.name
        expected_shared = ["mesh-devils-advocate"] if manifest["agent_id"] in {"cos", "cro"} else []
        assert manifest.get("shared_skills", []) == expected_shared, path.name
        assert builder.get("shared_skills", []) == expected_shared, path.name


def test_mcp_package_matches_mesh_local_stdio_pattern() -> None:
    required = {
        "README.md",
        "package.json",
        "package-lock.json",
        "tsconfig.json",
        "src/index.ts",
        "src/server.ts",
        "src/python-bridge.ts",
        "scripts/smoke-test.mjs",
    }
    for relative in required:
        assert (MCP_DIR / relative).is_file(), relative

    package = json.loads((MCP_DIR / "package.json").read_text())
    package_lock = json.loads((MCP_DIR / "package-lock.json").read_text())
    assert package["name"] == "@meshdigitalio/mesh-cos-mcp"
    assert package["version"] == RELEASE
    assert package_lock["version"] == RELEASE
    assert package_lock["packages"][""]["version"] == RELEASE
    assert package["scripts"]["check"]
    assert package["scripts"]["smoke"]
    assert package["dependencies"]["@modelcontextprotocol/sdk"]


def test_builder_and_skill_docs_require_local_stdio_not_remote_https() -> None:
    prompt = (ROOT / "chatgpt" / "workspace-agent-builder-prompt.md").read_text()
    assert "local stdio" in prompt.lower()
    assert "mcp/dist/index.js" in prompt
    assert "MESH_COS_AGENT_ID" in prompt
    assert "MESH_COS_LEDGER_PATH" in prompt
    assert "MESH_COS_MCP_SERVER_URL" not in prompt
    assert "10 agents" in prompt
    assert "Mesh Devil's Advocate" in prompt

    for skill_dir in (ROOT / "chatgpt" / "skills").iterdir():
        if not skill_dir.is_dir():
            continue
        readiness = (skill_dir / "references" / "production-readiness.md").read_text()
        assert "local stdio" in readiness.lower(), skill_dir.name
        assert "MESH_COS_MCP_SERVER_URL" not in readiness, skill_dir.name


def test_ci_certifies_python_and_local_stdio_mcp_release_gates() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert "actions/setup-node" in ci
    assert "npm ci" in ci
    assert "npm run check" in ci
    assert "working-directory: mcp" in ci
    assert "--cov-fail-under=100" in ci
