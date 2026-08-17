from dataclasses import dataclass
from .security import authorize_source
@dataclass(frozen=True,slots=True)
class AnswerDisposition: disposition:str; reason:str
def decide(*,known_fact:bool,source_accessible:bool,established_policy:bool,reversible:bool,requires_judgment:bool,ceo_authority:bool,requester_permissions:set[str],source_class:str="approved")->AnswerDisposition:
    if not authorize_source(requester_permissions,source_class):return AnswerDisposition("BLOCKED_BY_ACCESS","Requester lacks source permission")
    if ceo_authority:return AnswerDisposition("ESCALATED","CEO authority required")
    if known_fact and source_accessible:return AnswerDisposition("ANSWERED","Known authorized fact")
    if established_policy and reversible:return AnswerDisposition("ANSWERED","Established delegated policy")
    if requires_judgment:return AnswerDisposition("RECOMMENDATION_PROVIDED","Bounded judgment required")
    return AnswerDisposition("BLOCKED_BY_EVIDENCE","Insufficient authoritative evidence")
