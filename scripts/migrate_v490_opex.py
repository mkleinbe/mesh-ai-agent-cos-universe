#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


registry_path = ROOT / "agents/registry.json"
registry = json.loads(registry_path.read_text(encoding="utf-8"))
capability = {
    "capability": "mesh-opex-bot",
    "display_name": "Mesh OpEx Bot",
    "type": "shared_skill",
    "deployment": "EXTERNAL_SHARED_SKILL",
    "consumers": ["coo"],
    "authority": "OPERATIONAL_EXCELLENCE_ADVISORY_ONLY",
    "canonical_facts_modified": False,
    "external_action_included": False,
    "request_contract": "mesh.opex.request.v1",
    "response_contract": "mesh.opex.handoff.v1",
    "rule": "Provide Operational Excellence advisory evidence without replacing COO delivery feasibility, CoS TaskLedger/work-graph authority, CFO financial truth, AgentOps workforce-health authority, or qualified-human regulatory, clinical, legal, security, staffing, and consequential decision authority.",
}
shared = registry.setdefault("shared_capabilities", [])
shared[:] = [item for item in shared if item.get("capability") != "mesh-opex-bot"] + [capability]
coo = next(item for item in registry["agents"] if item["agent_id"] == "coo")
if "mesh-opex-bot" not in coo.setdefault("skills", []):
    coo["skills"].append("mesh-opex-bot")
registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

manifest_path = ROOT / "chatgpt/workspace-agents/coo.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["shared_skills"] = ["mesh-opex-bot"]
manifest["builder_configuration"]["shared_skills"] = ["mesh-opex-bot"]
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

role_path = ROOT / "chatgpt/skills/mesh-coo/references/role-contract.md"
role = role_path.read_text(encoding="utf-8")
if "## Mesh OpEx Bot shared capability" not in role:
    role += """

## Mesh OpEx Bot shared capability

`mesh-opex-bot` is an external shared Skill available only to the COO in Phase 1. Invoke it for specialist Operational Excellence diagnosis, minimum-sufficient method selection, improvement-system design, quality/reliability analysis, or AI-enabled operations redesign.

Request contract: `mesh.opex.request.v1`. Response/handoff contract: `mesh.opex.handoff.v1`. The capability is advisory only and cannot modify canonical facts, execute external actions, own TaskLedger state, confirm staffing or capacity, validate financial truth, govern agent workforce health, or issue regulatory, clinical, legal, or security conclusions.

COO retains delivery feasibility, capacity, staffing/resource readiness, partner capacity, dependencies, and operational constraints. CoS retains TaskLedger and work-graph orchestration. CFO retains financial truth and benefit validation. AgentOps retains agent workforce health and telemetry. Qualified humans retain regulated and consequential authority. If the shared Skill is unavailable, preserve the request as a bounded handoff and do not fabricate an OpEx result.
"""
role_path.write_text(role, encoding="utf-8")

checker_path = ROOT / "scripts/check-chatgpt-packages.py"
checker = checker_path.read_text(encoding="utf-8")
checker = checker.replace('ANALYTICS_CONSUMERS = {"cfo"}\n', 'ANALYTICS_CONSUMERS = {"cfo"}\nOPEX_CONSUMERS = {"coo"}\n')
checker = checker.replace(
    'require(set(shared) == {"mesh-devils-advocate", "mesh-data-analytics"}, "External Phase 1 shared Skill set drifted")',
    'require(set(shared) == {"mesh-devils-advocate", "mesh-data-analytics", "mesh-opex-bot"}, "External Phase 1 shared Skill set drifted")',
)
anchor = 'require(analytics["external_action_included"] is False, "Shared analytics cannot execute external actions")\n'
if 'opex = shared["mesh-opex-bot"]' not in checker:
    checker = checker.replace(
        anchor,
        anchor
        + 'opex = shared["mesh-opex-bot"]\n'
        + 'require(opex["deployment"] == "EXTERNAL_SHARED_SKILL", "Mesh OpEx Bot deployment drifted")\n'
        + 'require(set(opex["consumers"]) == OPEX_CONSUMERS, "Mesh OpEx Bot consumers drifted")\n'
        + 'require(opex["authority"] == "OPERATIONAL_EXCELLENCE_ADVISORY_ONLY", "Mesh OpEx Bot authority drifted")\n'
        + 'require(opex["canonical_facts_modified"] is False, "Mesh OpEx Bot cannot modify canonical facts")\n'
        + 'require(opex["external_action_included"] is False, "Mesh OpEx Bot cannot execute external actions")\n'
        + 'require(opex["request_contract"] == "mesh.opex.request.v1", "Mesh OpEx Bot request contract drifted")\n'
        + 'require(opex["response_contract"] == "mesh.opex.handoff.v1", "Mesh OpEx Bot response contract drifted")\n',
    )
expected_anchor = '    if agent_id in ANALYTICS_CONSUMERS:\n        expected_shared.append("mesh-data-analytics")\n'
if 'if agent_id in OPEX_CONSUMERS:' not in checker:
    checker = checker.replace(expected_anchor, expected_anchor + '    if agent_id in OPEX_CONSUMERS:\n        expected_shared.append("mesh-opex-bot")\n')
entitlement_anchor = '    require(("mesh-data-analytics" in record.get("skills", [])) is (agent_id in ANALYTICS_CONSUMERS), f"{agent_id}: Mesh Data Analytics entitlement drifted")\n'
if 'Mesh OpEx Bot entitlement drifted' not in checker:
    checker = checker.replace(entitlement_anchor, entitlement_anchor + '    require(("mesh-opex-bot" in record.get("skills", [])) is (agent_id in OPEX_CONSUMERS), f"{agent_id}: Mesh OpEx Bot entitlement drifted")\n')
checker_path.write_text(checker, encoding="utf-8")

readme_path = ROOT / "README.md"
readme = readme_path.read_text(encoding="utf-8").replace(
    "**Current repository release: `v4.8.4 Release Record Correction`.",
    "**Current repository release: `v4.9.0 Mesh OpEx Bot Shared Capability Integration`.",
)
readme_path.write_text(readme, encoding="utf-8")

docs_index_path = ROOT / "docs/README.md"
docs_index = docs_index_path.read_text(encoding="utf-8").replace(
    "Current repository release: **`v4.8.4 Release Record Correction`**.",
    "Current repository release: **`v4.9.0 Mesh OpEx Bot Shared Capability Integration`**.",
)
docs_index_path.write_text(docs_index, encoding="utf-8")

release_path = ROOT / "RELEASE.md"
release = release_path.read_text(encoding="utf-8")
heading = "# v4.9.0 Mesh OpEx Bot Shared Capability Integration\n"
if not release.startswith(heading):
    release = heading + """

`v4.9.0 Mesh OpEx Bot Shared Capability Integration` adds the external governed `mesh-opex-bot` capability to the COO without creating an eleventh agent or changing runtime authority.

Canonical Phase 1 authority/runtime contract: `4.0.0`, unchanged.  
Production QNAP deployment: `4.4.0`, unchanged.  
Registered organization: exactly 10 agents, unchanged.

The COO is the sole Phase 1 consumer. The shared Skill is advisory only, modifies no canonical facts, executes no external action, and uses `mesh.opex.request.v1` and `mesh.opex.handoff.v1`. COO retains delivery feasibility/capacity/staffing authority, CoS retains TaskLedger and work-graph orchestration, CFO retains financial truth, AgentOps retains agent-workforce health, and qualified humans retain regulated and consequential decisions.

v4.8.4 becomes historical read-only verification. v4.9.0 is the sole active exact-SHA SemVer publisher.

See `docs/release-v4.9.0-mesh-opex-bot-integration.md`, `docs/security-review-v4.9.0-mesh-opex-bot-integration.md`, `docs/verification-v4.9.0-mesh-opex-bot-integration.md`, `docs/gap-audit-v4.9.0-mesh-opex-bot-integration.md`, and `CHANGELOG-v4.9.0.md`.

""" + release
release_path.write_text(release, encoding="utf-8")

write("CHANGELOG-v4.9.0.md", """# Changelog v4.9.0

## Added
- External governed `mesh-opex-bot` shared capability for the COO only.
- Request/response contract projection for `mesh.opex.request.v1` and `mesh.opex.handoff.v1`.
- Workspace-agent, role-contract, package-drift, and regression coverage for the shared capability.

## Preserved
- Exactly ten Phase 1 agents.
- Canonical runtime authority contract 4.0.0 and production QNAP 4.4.0.
- COO, CoS, CFO, AgentOps, and qualified-human authority boundaries.
- No canonical-fact mutation or external-action authority for Mesh OpEx Bot.
""")
write("docs/release-v4.9.0-mesh-opex-bot-integration.md", """# v4.9.0 Mesh OpEx Bot Shared Capability Integration

Release date: September 13, 2026

This repository release integrates `mesh-opex-bot` as an external shared Skill consumed only by the COO. It does not add an agent principal, change TaskLedger ownership, change MCP transport, change production QNAP 4.4.0, or alter the canonical 4.0.0 authority/runtime contract.

The capability is advisory only. It cannot modify canonical facts or execute external action. COO retains delivery feasibility, capacity, staffing/resource readiness, dependencies, partner capacity, and operating constraints. CoS retains enterprise work-graph and TaskLedger authority. CFO retains financial truth and benefit validation. AgentOps retains agent workforce health and telemetry. Qualified humans retain regulated and consequential decision authority.

v4.8.4 is retired to manual read-only historical verification. v4.9.0 becomes the sole exact-SHA SemVer publisher after all verification gates pass.
""")
write("docs/security-review-v4.9.0-mesh-opex-bot-integration.md", """# v4.9.0 Security Review

Applicability: **TARGETED**

Sensitive surface: shared Skill entitlement and AI-native delegation/composition boundary. No new network, OAuth, credential, secret, persistence, or external-write surface is introduced.

Verified security properties:
- `mesh-opex-bot` remains a Skill, never an agent principal.
- Consumer scope is exactly `coo`.
- `canonical_facts_modified` is false.
- `external_action_included` is false.
- COO, CoS, CFO, AgentOps, and qualified-human authority remains explicit.
- Missing shared Skill availability degrades to a bounded handoff, never fabricated execution.
- Existing MCP allowlists and human-only operations remain unchanged.

Codex Security is not claimed unless separately evidenced. Repository tests, package drift checks, and independent verification provide the available bounded evidence for this change.
""")
write("docs/verification-v4.9.0-mesh-opex-bot-integration.md", """# v4.9.0 Verification

Required release proof:
- exactly 10 registered agents;
- no OpEx agent principal;
- one `mesh-opex-bot` external shared capability;
- COO is the sole consumer and has the matching Skill entitlement;
- request contract `mesh.opex.request.v1` and response contract `mesh.opex.handoff.v1`;
- canonical-fact mutation and external action remain false;
- CoS, CFO, AgentOps, COO, and human authority boundaries remain intact;
- package-drift and repository regression suites pass;
- v4.8.4 is historical read-only and v4.9.0 is the sole exact-SHA publisher;
- after merge, `main == tag v4.9.0 == GitHub Release target`.
""")
write("docs/gap-audit-v4.9.0-mesh-opex-bot-integration.md", """# v4.9.0 Gap Audit

| Requirement | State |
| --- | --- |
| Exactly ten agents | REQUIRED/PASS GATE |
| OpEx Bot is a shared Skill, not an agent | REQUIRED/PASS GATE |
| COO-only entitlement | REQUIRED/PASS GATE |
| No canonical mutation or external action | REQUIRED/PASS GATE |
| Preserve CoS/CFO/AgentOps/COO/human authority | REQUIRED/PASS GATE |
| Governed request/handoff contracts | REQUIRED/PASS GATE |
| v4.8.4 retired as publisher | REQUIRED/PASS GATE |
| v4.9.0 exact-SHA release | RELEASE GATE |
""")
write("tests/evaluations/test_opex_shared_capability_v490.py", """import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_opex_shared_capability_preserves_ten_agent_topology_and_authority() -> None:
    registry = json.loads((ROOT / 'agents/registry.json').read_text())
    agents = {item['agent_id']: item for item in registry['agents']}
    assert len(agents) == 10
    assert 'opex' not in agents and 'mesh-opex-bot' not in agents
    shared = [item for item in registry['shared_capabilities'] if item['capability'] == 'mesh-opex-bot']
    assert len(shared) == 1
    cap = shared[0]
    assert cap['type'] == 'shared_skill'
    assert cap['deployment'] == 'EXTERNAL_SHARED_SKILL'
    assert cap['consumers'] == ['coo']
    assert cap['authority'] == 'OPERATIONAL_EXCELLENCE_ADVISORY_ONLY'
    assert cap['canonical_facts_modified'] is False
    assert cap['external_action_included'] is False
    assert cap['request_contract'] == 'mesh.opex.request.v1'
    assert cap['response_contract'] == 'mesh.opex.handoff.v1'
    assert 'mesh-opex-bot' in agents['coo']['skills']
    for agent_id, record in agents.items():
        assert ('mesh-opex-bot' in record.get('skills', [])) is (agent_id == 'coo')


def test_coo_projection_and_fallback_are_governed() -> None:
    manifest = json.loads((ROOT / 'chatgpt/workspace-agents/coo.json').read_text())
    assert manifest['shared_skills'] == ['mesh-opex-bot']
    assert manifest['builder_configuration']['shared_skills'] == ['mesh-opex-bot']
    skill = (ROOT / 'chatgpt/skills/mesh-coo/SKILL.md').read_text()
    role = (ROOT / 'chatgpt/skills/mesh-coo/references/role-contract.md').read_text()
    for text in (skill, role):
        assert 'mesh-opex-bot' in text
        assert 'mesh.opex.request.v1' in text
        assert 'mesh.opex.handoff.v1' in text
        assert 'canonical facts' in text.lower()
        assert 'external action' in text.lower()
        assert 'CoS' in text and 'CFO' in text and 'AgentOps' in text
    assert 'do not fabricate' in skill.lower()
""")

historical_path = ROOT / "tests/evaluations/test_historical_release_workflows_v483.py"
historical = historical_path.read_text(encoding="utf-8")
historical = historical.replace(
    '"4.6.0", "4.7.0", "4.8.0", "4.8.1", "4.8.2", "4.8.3",',
    '"4.6.0", "4.7.0", "4.8.0", "4.8.1", "4.8.2", "4.8.3", "4.8.4",',
)
start = historical.index("def test_v484_is_the_only_semver_release_publisher()")
historical = historical[:start] + '''def test_v490_is_the_only_semver_release_publisher() -> None:\n    current = _active_yaml_text((WORKFLOWS / "release-v4.9.0.yml").read_text(encoding="utf-8"))\n    assert "branches: [main]" in current\n    assert "pull_request:" in current\n    assert "gh release create v4.9.0" in current\n    assert "--target \\\"$GITHUB_SHA\\\"" in current\n    assert "permissions:\\n  contents: read" in current\n    assert "contents: write" in current\n'''
historical_path.write_text(historical, encoding="utf-8")

write("tests/evaluations/test_release_record_correction_v484.py", '''from pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\nWORKFLOWS = ROOT / ".github" / "workflows"\n\ndef _active_yaml_text(path: Path) -> str:\n    return "\\n".join(line for line in path.read_text(encoding="utf-8").splitlines() if not line.lstrip().startswith("#"))\n\ndef test_v483_release_records_explicitly_include_v460_retirement() -> None:\n    for path in (ROOT / "CHANGELOG-v4.8.3.md", ROOT / "docs/release-v4.8.3-historical-publisher-retirement.md", ROOT / "docs/gap-audit-v4.8.3-historical-publisher-retirement.md"):\n        text = path.read_text(encoding="utf-8")\n        assert "v4.6.0" in text, path\n        assert "v4.8.2" in text, path\n\ndef test_v484_is_historical_and_v490_is_the_only_current_publisher() -> None:\n    historical = _active_yaml_text(WORKFLOWS / "release-v4.8.4.yml")\n    assert "workflow_dispatch:" in historical\n    assert "branches: [main]" not in historical\n    assert "pull_request:" not in historical\n    assert "gh release create" not in historical\n    assert "contents: write" not in historical\n    current = _active_yaml_text(WORKFLOWS / "release-v4.9.0.yml")\n    assert "branches: [main]" in current\n    assert "pull_request:" in current\n    assert "gh release create v4.9.0" in current\n    assert "--target \\\"$GITHUB_SHA\\\"" in current\n    assert "contents: write" in current\n\ndef test_v490_release_identity_preserves_runtime_and_topology() -> None:\n    readme = (ROOT / "README.md").read_text(encoding="utf-8")\n    release = (ROOT / "RELEASE.md").read_text(encoding="utf-8")\n    docs_index = (ROOT / "docs/README.md").read_text(encoding="utf-8")\n    for text in (readme, release, docs_index):\n        assert "v4.9.0 Mesh OpEx Bot Shared Capability Integration" in text\n        assert "4.0.0" in text\n        assert "4.4.0" in text\n    assert "exactly 10" in readme.lower()\n''')

print("v4.9.0 OpEx integration migration applied")
