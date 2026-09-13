#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'scripts/check-runtime-doc-drift.py'
text = path.read_text(encoding='utf-8')

text = text.replace(
    'require(set(shared) == {"mesh-devils-advocate", "mesh-data-analytics"}, "External Phase 1 shared Skill set drifted")',
    'require(set(shared) == {"mesh-devils-advocate", "mesh-data-analytics", "mesh-opex-bot"}, "External Phase 1 shared Skill set drifted")',
    1,
)

analytics_line = 'require(analytics["external_action_included"] is False, "Mesh Data Analytics cannot execute external actions")'
if 'opex = shared["mesh-opex-bot"]' not in text:
    text = text.replace(
        analytics_line,
        analytics_line + '''
opex = shared["mesh-opex-bot"]
require(set(opex["consumers"]) == {"coo"}, "Mesh OpEx Bot consumers drifted")
require(opex["authority"] == "OPERATIONAL_EXCELLENCE_ADVISORY_ONLY", "Mesh OpEx Bot authority drifted")
require(opex["canonical_facts_modified"] is False, "Mesh OpEx Bot cannot modify canonical facts")
require(opex["external_action_included"] is False, "Mesh OpEx Bot cannot execute external actions")
require(opex["request_contract"] == "mesh.opex.request.v1", "Mesh OpEx Bot request contract drifted")
require(opex["response_contract"] == "mesh.opex.handoff.v1", "Mesh OpEx Bot response contract drifted")''',
        1,
    )

required = [
    '{"mesh-devils-advocate", "mesh-data-analytics", "mesh-opex-bot"}',
    'opex = shared["mesh-opex-bot"]',
    'set(opex["consumers"]) == {"coo"}',
    'OPERATIONAL_EXCELLENCE_ADVISORY_ONLY',
    'mesh.opex.request.v1',
    'mesh.opex.handoff.v1',
]
missing = [token for token in required if token not in text]
if missing:
    raise SystemExit(f'v4.9.0 runtime drift migration incomplete: {missing}')

path.write_text(text, encoding='utf-8')
print('v4.9.0 runtime/documentation drift migration applied')
