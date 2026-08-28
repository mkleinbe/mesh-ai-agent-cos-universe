#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "mesh_cos" / "mcp_runtime.py"
SELF = ROOT / "scripts" / "apply_v440_surgical_patch.py"
WORKFLOW = ROOT / ".github" / "workflows" / "v440-surgical-patch.yml"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


text = RUNTIME.read_text()

text = replace_once(
    text,
    '''        tool_name = str(args["tool_name"])
        if tool_name not in OWNER_EXECUTABLE_TOOLS:
            raise PermissionError("Tool is not available through delegated owner execution")
        if tool_name in OWNER_NESTED_DELEGATION_TOOLS and not self._delegation_allows_nested_work(delegation):
            raise PermissionError("Delegation does not authorize nested delegation work")
''',
    '''        tool_name = str(args["tool_name"])
        if tool_name in HUMAN_ONLY_TOOLS or tool_name == "task.verify":
            raise PermissionError("Owner execution cannot invoke human-only or verifier MCP tools")
        if tool_name not in OWNER_EXECUTABLE_TOOLS:
            raise PermissionError("Tool is not available through delegated owner execution")
        if tool_name in OWNER_NESTED_DELEGATION_TOOLS and not self._delegation_allows_nested_work(delegation):
            raise PermissionError("Delegation does not authorize nested delegation work")
''',
    "move-human-only-denial-before-tool-surface",
)

text = replace_once(
    text,
    '''        if tool_name in HUMAN_ONLY_TOOLS or tool_name == "task.verify":
            raise PermissionError("Owner execution cannot invoke human-only or verifier MCP tools")
        self.policy.authorize(owner_id, tool_name)

        raw_arguments = dict(args.get("arguments", {}))
''',
    '''        self.policy.authorize(owner_id, tool_name)

        raw_arguments = dict(args.get("arguments", {}))
''',
    "remove-duplicate-human-only-denial",
)

text = replace_once(
    text,
    '''            if capability not in permitted_capabilities:
                raise PermissionError("Capability is not explicitly permitted by the canonical delegation")
''',
    '''            if capability not in permitted_capabilities:
                raise PermissionError(
                    "Capability not allowed: capability is not explicitly permitted by the canonical delegation"
                )
''',
    "capability-denial-message",
)

fingerprint_block = '''        request_fingerprint = hashlib.sha256(
            json.dumps(
                {
                    "protocol_version": protocol_version,
                    "delegation_id": delegation_id,
                    "task_id": task_id,
                    "tool_name": tool_name,
                    "arguments": owner_args,
                    "approval_references": approval_references,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        record_id = f"{delegation_id}:{idempotency_key}"
'''

fingerprint_replacement = '''        request_fingerprint = hashlib.sha256(
            json.dumps(
                {
                    "protocol_version": protocol_version,
                    "delegation_id": delegation_id,
                    "task_id": task_id,
                    "tool_name": tool_name,
                    "arguments": owner_args,
                    "approval_references": approval_references,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        accepted_request_fingerprints = {request_fingerprint}
        if not approval_references:
            legacy_request_fingerprint = hashlib.sha256(
                json.dumps(
                    {
                        "delegation_id": delegation_id,
                        "task_id": task_id,
                        "tool_name": tool_name,
                        "arguments": owner_args,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            accepted_request_fingerprints.add(legacy_request_fingerprint)
        record_id = f"{delegation_id}:{idempotency_key}"
'''
text = replace_once(text, fingerprint_block, fingerprint_replacement, "legacy-fingerprint-derivation")

text = replace_once(
    text,
    '''        if existing is not None:
            if existing.get("request_fingerprint") != request_fingerprint:
                raise PermissionError("Owner execution idempotency key cannot be reused for another request")
            if existing.get("status") == "OWNER_RESULT_RECORDED":
                return dict(existing["response"])
''',
    '''        if existing is not None:
            if existing.get("request_fingerprint") not in accepted_request_fingerprints:
                raise PermissionError("Owner execution idempotency key cannot be reused for another request")
            if existing.get("status") == "OWNER_RESULT_RECORDED":
                return dict(existing["response"])
''',
    "legacy-existing-fingerprint",
)

text = replace_once(
    text,
    '''            if (
                prior
                and prior.get("request_fingerprint") == request_fingerprint
                and prior.get("status") == "OWNER_RESULT_RECORDED"
            ):
''',
    '''            if (
                prior
                and prior.get("request_fingerprint") in accepted_request_fingerprints
                and prior.get("status") == "OWNER_RESULT_RECORDED"
            ):
''',
    "legacy-concurrent-claim-fingerprint",
)

RUNTIME.write_text(text)
SELF.unlink()
WORKFLOW.unlink()
