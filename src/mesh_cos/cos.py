from __future__ import annotations

from .authority import classify
from .models import AuthorityLevel

ROUTE_BY_DOMAIN = {
    "commercial": "cro",
    "finance": "cfo",
    "delivery": "coo",
    "marketing": "cmo",
    "team_question": "answer-desk",
    "agent_health": "agentops",
    "external_message": "message-ops",
    "challenge": "devils-advocate",
}


def route_work(domain: str) -> str:
    return ROUTE_BY_DOMAIN.get(domain, "cos")


def should_escalate(
    action: str,
    *,
    requested_level: AuthorityLevel,
    material: bool = False,
    reversible: bool = True,
    external: bool = False,
    low_confidence: bool = False,
) -> bool:
    decision = classify(
        action,
        requested_level,
        material=material,
        reversible=reversible,
        external=external,
        low_confidence=low_confidence,
    )
    return decision.human_approval_required
