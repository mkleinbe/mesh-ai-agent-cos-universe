#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'scripts/check-chatgpt-packages.py'
text = path.read_text(encoding='utf-8')

if 'OPEX_CONSUMERS = {"coo"}' not in text:
    text = text.replace(
        'ANALYTICS_CONSUMERS = {"cfo"}',
        'ANALYTICS_CONSUMERS = {"cfo"}\nOPEX_CONSUMERS = {"coo"}',
        1,
    )

text = text.replace(
    'require(set(shared) == {"mesh-devils-advocate", "mesh-data-analytics"}, "External Phase 1 shared Skill set drifted")',
    'require(set(shared) == {"mesh-devils-advocate", "mesh-data-analytics", "mesh-opex-bot"}, "External Phase 1 shared Skill set drifted")',
    1,
)

analytics_line = 'require(analytics["external_action_included"] is False, "Shared analytics cannot execute external actions")'
if 'opex = shared["mesh-opex-bot"]' not in text:
    text = text.replace(
        analytics_line,
        analytics_line + '''
opex = shared["mesh-opex-bot"]
require(opex["deployment"] == "EXTERNAL_SHARED_SKILL", "Mesh OpEx Bot deployment drifted")
require(set(opex["consumers"]) == OPEX_CONSUMERS, "Mesh OpEx Bot consumers drifted")
require(opex["authority"] == "OPERATIONAL_EXCELLENCE_ADVISORY_ONLY", "Mesh OpEx Bot authority drifted")
require(opex["canonical_facts_modified"] is False, "Mesh OpEx Bot cannot modify canonical facts")
require(opex["external_action_included"] is False, "Mesh OpEx Bot cannot execute external actions")
require(opex["request_contract"] == "mesh.opex.request.v1", "Mesh OpEx Bot request contract drifted")
require(opex["response_contract"] == "mesh.opex.handoff.v1", "Mesh OpEx Bot response contract drifted")''',
        1,
    )

analytics_projection = '''    if agent_id in ANALYTICS_CONSUMERS:
        expected_shared.append("mesh-data-analytics")'''
if 'if agent_id in OPEX_CONSUMERS:' not in text:
    text = text.replace(
        analytics_projection,
        analytics_projection + '''
    if agent_id in OPEX_CONSUMERS:
        expected_shared.append("mesh-opex-bot")''',
        1,
    )

analytics_entitlement = '    require(("mesh-data-analytics" in record.get("skills", [])) is (agent_id in ANALYTICS_CONSUMERS), f"{agent_id}: Mesh Data Analytics entitlement drifted")'
if 'Mesh OpEx Bot entitlement drifted' not in text:
    text = text.replace(
        analytics_entitlement,
        analytics_entitlement + '\n    require(("mesh-opex-bot" in record.get("skills", [])) is (agent_id in OPEX_CONSUMERS), f"{agent_id}: Mesh OpEx Bot entitlement drifted")',
        1,
    )

required = [
    'OPEX_CONSUMERS = {"coo"}',
    '{"mesh-devils-advocate", "mesh-data-analytics", "mesh-opex-bot"}',
    'opex = shared["mesh-opex-bot"]',
    'if agent_id in OPEX_CONSUMERS:',
    'Mesh OpEx Bot entitlement drifted',
]
missing = [token for token in required if token not in text]
if missing:
    raise SystemExit(f'v4.9.0 checker migration incomplete: {missing}')

path.write_text(text, encoding='utf-8')
print('v4.9.0 package drift checker migration applied')
