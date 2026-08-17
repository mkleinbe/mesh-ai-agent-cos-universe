from __future__ import annotations

from copy import deepcopy
from typing import Any

AGENTS: dict[str, dict[str, Any]] = {
    "cos": {"display_name":"Chief of Staff","parent_agent_id":None,"agent_type":"executive","accountable_domain":"executive orchestration","status":"ACTIVE","decision_authority":3,"skills":["mesh-ppmd-bot"],"prohibited_actions":["canonical_finance","external_send","commercial_commitment"],"max_delegation_depth":2},
    "agentops": {"display_name":"AgentOps Controller","parent_agent_id":"cos","agent_type":"controller","accountable_domain":"agent operations and observability","status":"ACTIVE","decision_authority":2,"skills":[],"prohibited_actions":["business_strategy"],"max_delegation_depth":0},
    "answer-desk": {"display_name":"Answer & Decision Desk","parent_agent_id":"cos","agent_type":"operations","accountable_domain":"authorized team questions and routing","status":"ACTIVE","decision_authority":2,"skills":["mesh-firm-360"],"prohibited_actions":["private_dm_exposure","confidential_client_exposure","financial_exposure","privileged_context_exposure"],"max_delegation_depth":0},
    "cro": {"display_name":"CRO","parent_agent_id":"cos","agent_type":"executive","accountable_domain":"commercial interpretation and pursuit strategy","status":"ACTIVE","decision_authority":3,"skills":["mesh-revenue-intelligence","mesh-firm-360","mesh-competitive-displacement-engine","mesh-gtm-orchestrator","mesh-buyer-psychology","mesh-sales-messaging"],"prohibited_actions":["pricing_approval","discount_approval","contract_commitment","final_scope"],"max_delegation_depth":1},
    "cfo": {"display_name":"CFO v1, Engagement Finance / FP&A","parent_agent_id":"cos","agent_type":"executive","accountable_domain":"engagement economics","status":"ACTIVE","decision_authority":3,"authoritative_sources":["Mesh Proposals - Engagement P&L Tracker"],"skills":[],"prohibited_actions":["enterprise_gl_claim","bank_balance_claim","tax_position_claim","audited_financial_claim"],"max_delegation_depth":1},
    "coo": {"display_name":"COO v1","parent_agent_id":"cos","agent_type":"executive","accountable_domain":"delivery feasibility and resource readiness","status":"ACTIVE","decision_authority":3,"authoritative_sources":["Capabilities Partner & Consultant Tracker"],"skills":[],"prohibited_actions":["treat_stale_availability_as_confirmed"],"max_delegation_depth":1},
    "consultant-network-steward": {"display_name":"Consultant Network Steward","parent_agent_id":"coo","agent_type":"specialist","accountable_domain":"consultant readiness verification","status":"ACTIVE","decision_authority":2,"skills":[],"prohibited_actions":["confirm_stale_availability"],"max_delegation_depth":0},
    "cmo": {"display_name":"CMO","parent_agent_id":"cos","agent_type":"executive","accountable_domain":"marketing strategy and execution","status":"ACTIVE","decision_authority":3,"skills":["mesh-marketing-messaging","mesh-messaging-orchestrator","mesh-executive-communications"],"prohibited_actions":["public_publish_without_approval"],"max_delegation_depth":1},
    "vp-content": {"display_name":"VP Content","parent_agent_id":"cmo","agent_type":"specialist","accountable_domain":"content production execution","status":"ACTIVE","decision_authority":2,"skills":["mesh-marketing-messaging"],"prohibited_actions":["public_publish"],"max_delegation_depth":0},
    "devils-advocate": {"display_name":"Devil's Advocate","parent_agent_id":"cos","agent_type":"reviewer","accountable_domain":"independent challenge","status":"ACTIVE","decision_authority":1,"skills":["mesh-devils-advocate"],"prohibited_actions":["final_decision"],"max_delegation_depth":0},
    "message-ops": {"display_name":"Message Operations","parent_agent_id":"cos","agent_type":"operations","accountable_domain":"controlled approved communication execution","status":"ACTIVE","decision_authority":1,"skills":["mesh-message-operations"],"prohibited_actions":["consequential_external_send_without_approval"],"max_delegation_depth":0},
}

def get_agent(agent_id: str) -> dict[str, Any]:
    if agent_id not in AGENTS: raise KeyError(agent_id)
    return deepcopy(AGENTS[agent_id])

def validate_registry() -> None:
    for agent_id, record in AGENTS.items():
        parent = record.get("parent_agent_id")
        if parent and parent not in AGENTS: raise ValueError(f"Unknown parent for {agent_id}: {parent}")
        if record.get("status") not in {"SHADOW","ACTIVE","WATCH","RESTRICTED","QUARANTINED","RETIRED"}: raise ValueError(f"Invalid health state for {agent_id}")
