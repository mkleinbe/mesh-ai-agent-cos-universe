#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED_SET_OLD = '{"mesh-devils-advocate", "mesh-data-analytics"}'
SHARED_SET_NEW = '{"mesh-devils-advocate", "mesh-data-analytics", "mesh-opex-bot"}'


def replace(path: str, old: str, new: str, *, required: bool = True) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        if required and new not in text:
            raise SystemExit(f"missing migration anchor in {path}: {old!r}")
        return
    target.write_text(text.replace(old, new), encoding="utf-8")


# Shared-capability acceptance package.
path = ROOT / "tests/evaluations/test_chatgpt_workspace_agent_packages.py"
text = path.read_text(encoding="utf-8")
if 'SHARED_OPEX_CONSUMERS = {"coo"}' not in text:
    text = text.replace(
        'SHARED_ANALYTICS_CONSUMERS = {"cfo"}\n',
        'SHARED_ANALYTICS_CONSUMERS = {"cfo"}\nSHARED_OPEX_CONSUMERS = {"coo"}\n',
        1,
    )
text = text.replace(SHARED_SET_OLD, SHARED_SET_NEW)
if 'if agent_id in SHARED_OPEX_CONSUMERS:' not in text:
    text = text.replace(
        '    if agent_id in SHARED_ANALYTICS_CONSUMERS:\n        capabilities.append("mesh-data-analytics")\n',
        '    if agent_id in SHARED_ANALYTICS_CONSUMERS:\n        capabilities.append("mesh-data-analytics")\n'
        '    if agent_id in SHARED_OPEX_CONSUMERS:\n        capabilities.append("mesh-opex-bot")\n',
        1,
    )
analytics_anchor = '    assert analytics["external_action_included"] is False\n'
if 'opex = capabilities["mesh-opex-bot"]' not in text:
    text = text.replace(
        analytics_anchor,
        analytics_anchor
        + '    opex = capabilities["mesh-opex-bot"]\n'
        + '    assert opex["deployment"] == "EXTERNAL_SHARED_SKILL"\n'
        + '    assert set(opex["consumers"]) == SHARED_OPEX_CONSUMERS\n'
        + '    assert opex["authority"] == "OPERATIONAL_EXCELLENCE_ADVISORY_ONLY"\n'
        + '    assert opex["canonical_facts_modified"] is False\n'
        + '    assert opex["external_action_included"] is False\n'
        + '    assert opex["request_contract"] == "mesh.opex.request.v1"\n'
        + '    assert opex["response_contract"] == "mesh.opex.handoff.v1"\n',
        1,
    )
registry_anchor = '        assert ("mesh-devils-advocate" in record.get("skills", [])) is (agent_id in SHARED_CHALLENGE_CONSUMERS)\n'
if 'SHARED_OPEX_CONSUMERS)' not in text.split(registry_anchor, 1)[-1] if registry_anchor in text else True:
    if registry_anchor in text and 'Mesh OpEx' not in text[text.index(registry_anchor):text.index(registry_anchor)+500]:
        text = text.replace(
            registry_anchor,
            registry_anchor
            + '        assert ("mesh-data-analytics" in record.get("skills", [])) is (agent_id in SHARED_ANALYTICS_CONSUMERS)\n'
            + '        assert ("mesh-opex-bot" in record.get("skills", [])) is (agent_id in SHARED_OPEX_CONSUMERS)\n',
            1,
        )
path.write_text(text, encoding="utf-8")

# Historical enterprise consulting expectations now include the approved COO shared capability.
path = ROOT / "tests/evaluations/test_enterprise_consulting_skill_consumption_v470.py"
text = path.read_text(encoding="utf-8").replace(SHARED_SET_OLD, SHARED_SET_NEW)
text = text.replace('    assert records["coo"]["skills"] == []\n', '    assert records["coo"]["skills"] == ["mesh-opex-bot"]\n')
path.write_text(text, encoding="utf-8")

# Functional Method Expansion governance set remains ten agents while adding one shared capability.
replace("tests/evaluations/test_functional_method_expansion_v480.py", SHARED_SET_OLD, SHARED_SET_NEW)

# Local ChatGPT MCP projection recognizes the COO shared Skill without changing MCP identity or transport.
path = ROOT / "tests/evaluations/test_local_chatgpt_mcp_projection.py"
text = path.read_text(encoding="utf-8")
if 'if manifest["agent_id"] == "coo":' not in text:
    text = text.replace(
        '        if manifest["agent_id"] == "cfo":\n            expected_shared.append("mesh-data-analytics")\n',
        '        if manifest["agent_id"] == "cfo":\n            expected_shared.append("mesh-data-analytics")\n'
        '        if manifest["agent_id"] == "coo":\n            expected_shared.append("mesh-opex-bot")\n',
        1,
    )
path.write_text(text, encoding="utf-8")

# Canonical role-model consistency recognizes the third shared capability and its hard boundaries.
path = ROOT / "tests/evaluations/test_phase1_role_model_consistency.py"
text = path.read_text(encoding="utf-8").replace(SHARED_SET_OLD, SHARED_SET_NEW)
anchor = '    assert shared["mesh-data-analytics"]["consumers"] == ["cfo"]\n'
if 'shared["mesh-opex-bot"]' not in text:
    text = text.replace(
        anchor,
        anchor
        + '    assert shared["mesh-opex-bot"]["authority"] == "OPERATIONAL_EXCELLENCE_ADVISORY_ONLY"\n'
        + '    assert shared["mesh-opex-bot"]["consumers"] == ["coo"]\n'
        + '    assert shared["mesh-opex-bot"]["canonical_facts_modified"] is False\n'
        + '    assert shared["mesh-opex-bot"]["external_action_included"] is False\n'
        + '    assert records["coo"]["skills"] == ["mesh-opex-bot"]\n',
        1,
    )
path.write_text(text, encoding="utf-8")

# Make fallback language explicitly testable rather than relying on paraphrase.
skill = ROOT / "chatgpt/skills/mesh-coo/SKILL.md"
text = skill.read_text(encoding="utf-8")
text = text.replace(
    'If the shared Skill is unavailable, preserve the request as a bounded handoff rather than fabricating an OpEx result.',
    'If the shared Skill is unavailable, preserve the request as a bounded handoff. Do not fabricate an OpEx result.',
)
skill.write_text(text, encoding="utf-8")

# Postconditions prove we changed only expected-state assertions, not the ten-agent boundary.
checks = {
    "tests/evaluations/test_chatgpt_workspace_agent_packages.py": [SHARED_SET_NEW, 'SHARED_OPEX_CONSUMERS = {"coo"}'],
    "tests/evaluations/test_enterprise_consulting_skill_consumption_v470.py": [SHARED_SET_NEW, 'records["coo"]["skills"] == ["mesh-opex-bot"]'],
    "tests/evaluations/test_functional_method_expansion_v480.py": [SHARED_SET_NEW, 'assert len(agents) == 10'],
    "tests/evaluations/test_local_chatgpt_mcp_projection.py": ['expected_shared.append("mesh-opex-bot")', 'assert len(manifests) == 10'],
    "tests/evaluations/test_phase1_role_model_consistency.py": [SHARED_SET_NEW, 'shared["mesh-opex-bot"]'],
    "chatgpt/skills/mesh-coo/SKILL.md": ['Do not fabricate an OpEx result.', 'A Skill is a capability, not an agent principal.'],
}
for rel, tokens in checks.items():
    body = (ROOT / rel).read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in body]
    if missing:
        raise SystemExit(f"v4.9.0 regression migration incomplete for {rel}: {missing}")

print("v4.9.0 regression expectations migrated without changing ten-agent authority")
