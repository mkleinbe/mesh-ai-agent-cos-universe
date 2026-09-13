import json
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
