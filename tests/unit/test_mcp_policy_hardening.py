from __future__ import annotations

from copy import deepcopy

import pytest

from mesh_cos.mcp_policy import WorkspaceAgentMCPPolicy


def contract() -> dict:
    return deepcopy(WorkspaceAgentMCPPolicy.from_file().contract)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda c: c.__setitem__("serialized_runtime", "unsafe.Runtime"), "serialized MCPRuntime"),
        (lambda c: c["security"].__setitem__("server_derived_agent_identity", False), "identity must be derived"),
        (lambda c: c["security"].__setitem__("human_principal_required_for_human_tools", False), "authenticated human"),
        (lambda c: c["security"].__setitem__("client_supplied_code_execution", True), "code execution"),
    ],
)
def test_strict_contract_rejects_missing_runtime_security_invariants(mutate, message: str) -> None:
    value = contract()
    mutate(value)
    with pytest.raises(ValueError, match=message):
        WorkspaceAgentMCPPolicy(value).validate()


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda c: c.__setitem__("transport", "REMOTE_HTTPS"), "LOCAL_STDIO"),
        (lambda c: c.__setitem__("local_runtime", None), "local_runtime"),
        (lambda c: c["local_runtime"].__setitem__("command", "python"), "command"),
        (lambda c: c["local_runtime"].__setitem__("args", ["wrong"]), "mcp/dist/index.js"),
        (lambda c: c["local_runtime"].__setitem__("agent_identity_env", "WRONG"), "MESH_COS_AGENT_ID"),
        (lambda c: c["local_runtime"].__setitem__("ledger_path_env", "WRONG"), "MESH_COS_LEDGER_PATH"),
        (lambda c: c["local_runtime"].__setitem__("python_bridge", "unsafe.bridge"), "mcp_stdio_bridge"),
        (lambda c: c["deployment"].__setitem__("chatgpt_runtime", "REMOTE"), "bundled local stdio"),
        (lambda c: c["deployment"].__setitem__("managed_remote", "REQUIRED"), "remain optional"),
        (lambda c: c.__setitem__("server_url_env", "MESH_COS_MCP_SERVER_URL"), "remote server URL"),
    ],
)
def test_strict_contract_rejects_local_transport_drift(mutate, message: str) -> None:
    value = contract()
    mutate(value)
    with pytest.raises(ValueError, match=message):
        WorkspaceAgentMCPPolicy(value).validate()


def test_strict_contract_rejects_human_tool_allowlist_defects() -> None:
    value = contract()
    value["human_tool_allowlist"] = ["unknown.tool"]
    with pytest.raises(ValueError, match="unknown MCP tools"):
        WorkspaceAgentMCPPolicy(value).validate()

    value = contract()
    value["human_tool_allowlist"] = []
    with pytest.raises(ValueError, match="must be explicitly allowlisted"):
        WorkspaceAgentMCPPolicy(value).validate()

    value = contract()
    value["agent_tool_allowlists"]["cos"].append("approval.record_decision")
    with pytest.raises(ValueError, match="cannot appear in agent allowlists"):
        WorkspaceAgentMCPPolicy(value).validate()


def test_strict_contract_rejects_incorrect_runtime_binding_class() -> None:
    value = contract()
    human = next(tool for tool in value["tools"] if tool["name"] == "approval.record_decision")
    human["runtime_binding"] = "mesh_cos.mcp_runtime.MCPRuntime.call_agent"
    with pytest.raises(ValueError, match="must bind to call_human"):
        WorkspaceAgentMCPPolicy(value).validate()

    value = contract()
    agent = next(tool for tool in value["tools"] if tool["name"] == "task.get")
    agent["runtime_binding"] = "mesh_cos.mcp_runtime.MCPRuntime.call_human"
    with pytest.raises(ValueError, match="must bind to call_agent"):
        WorkspaceAgentMCPPolicy(value).validate()


def test_human_authorization_denies_unknown_and_agent_tools() -> None:
    policy = WorkspaceAgentMCPPolicy.from_file()
    with pytest.raises(PermissionError, match="Unknown MCP tool"):
        policy.authorize_human("unknown.tool")
    with pytest.raises(PermissionError, match="not human-authorized"):
        policy.authorize_human("task.get")
    assert policy.authorize_human("approval.record_decision")["name"] == "approval.record_decision"
