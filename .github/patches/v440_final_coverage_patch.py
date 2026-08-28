from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}")
    target.write_text(text.replace(old, new, 1))


replace_once(
    "tests/evaluations/test_qnap_production_identity_v416.py",
    'assert "Build current-source QNAP CI candidate" in ci',
    'assert "Build current-source v4.4.0 candidate artifacts" in ci',
)

replace_once(
    "tests/evaluations/test_qnap_slack_approver_bootstrap_v4113.py",
    '''def test_v4113_and_v420_release_evidence_remain_historical_while_current_is_v430() -> None:\n''',
    '''def test_historical_release_evidence_remains_while_v440_is_candidate_and_v430_is_deployed() -> None:\n''',
)
replace_once(
    "tests/evaluations/test_qnap_slack_approver_bootstrap_v4113.py",
    '''    assert "v4.3.0 Cross-Agent Owner Execution" in readme\n    assert "Historical versioned documents remain retained as release-train evidence" in readme\n''',
    '''    assert "v4.4.0 Authority Closure" in readme\n    assert "Current deployed QNAP release remains `v4.3.0`" in readme\n    assert "Historical v4.3.x documents remain retained as release-train evidence" in readme\n''',
)

replace_once(
    "tests/evaluations/test_shared_devils_advocate_integration.py",
    '''    assert "# v4.3.0 Cross-Agent Owner Execution" in release_notes\n    assert "canonical Phase 1 authority/runtime contract remains **`4.0.0`**" in release_notes\n''',
    '''    assert "# v4.4.0 Authority Closure" in release_notes\n    assert "canonical Phase 1 authority/runtime contract remains **4.0.0**" in release_notes\n    assert "v4.3.0" in release_notes\n''',
)

replace_once(
    "tests/evaluations/test_shared_message_operations_refactor.py",
    '''    assert "# v4.3.0 Cross-Agent Owner Execution" in release\n    assert "canonical Phase 1 authority/runtime contract remains **`4.0.0`**" in release\n''',
    '''    assert "# v4.4.0 Authority Closure" in release\n    assert "canonical Phase 1 authority/runtime contract remains **4.0.0**" in release\n    assert "v4.3.0" in release\n''',
)

replace_once(
    "src/mesh_cos/mcp_runtime.py",
    "from typing import Any\n",
    "from typing import Any, cast\n",
)
replace_once(
    "src/mesh_cos/mcp_runtime.py",
    '''            if last_error is not None:\n                raise last_error\n''',
    '''            raise cast(PermissionError, last_error)\n''',
)

coverage_path = Path("tests/unit/test_v440_authority_edge_coverage.py")
coverage = coverage_path.read_text()
anchor = '''def test_owner_execution_requires_nonempty_idempotency_key() -> None:\n'''
insert = '''def test_owner_execution_rejects_unsupported_protocol_version() -> None:\n    runtime = MCPRuntime(TaskLedger())\n    with pytest.raises(PermissionError, match="Unsupported owner-execution protocol"):\n        runtime._delegation_execute_owner(\n            "cos",\n            {\n                "protocol_version": "mesh.cos.owner-execution.v999",\n                "delegation_id": "D1",\n                "task_id": "T1",\n                "tool_name": "task.get",\n                "arguments": {"task_id": "T1"},\n                "idempotency_key": "wrong-protocol",\n            },\n        )\n\n\n'''
if coverage.count(anchor) != 1:
    raise SystemExit(f"coverage anchor expected once, found {coverage.count(anchor)}")
coverage_path.write_text(coverage.replace(anchor, insert + anchor, 1))
