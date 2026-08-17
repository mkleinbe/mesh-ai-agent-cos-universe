from __future__ import annotations
from dataclasses import dataclass
DEFAULT_WEIGHTS={"outcome_achievement":.30,"first_pass_quality":.20,"escalation_judgment":.15,"evidence_governance":.10,"execution_reliability":.10,"ceo_leverage":.10,"efficiency":.05}
@dataclass(frozen=True,slots=True)
class PerformanceEvent:
    agent_id:str; task_id:str; category:str; score:float; severity:str="LOW"; reason:str=""
def score(events:list[PerformanceEvent],weights:dict[str,float]|None=None)->float:
    weights=weights or DEFAULT_WEIGHTS; grouped={}
    for e in events: grouped.setdefault(e.category,[]).append(e.score)
    weighted=used=0.0
    for c,w in weights.items():
        if grouped.get(c): weighted+=(sum(grouped[c])/len(grouped[c]))*w; used+=w
    return round(weighted/used,4) if used else 0.0
def recommendation(events:list[PerformanceEvent])->str:
    if any(e.severity=="CRITICAL" for e in events): return "QUARANTINE"
    s=score(events)
    if s<.30:return "RESTRICT"
    if s<.65:return "WATCH"
    if s>.90 and len(events)>=5:return "INCREASE_ROUTING"
    return "CONTINUE"
