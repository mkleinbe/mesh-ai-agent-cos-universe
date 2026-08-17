from __future__ import annotations
from datetime import datetime, timezone
from .models import TaskRecord
from .performance import PerformanceEvent,recommendation
def stalled(task:TaskRecord,now:datetime|None=None)->bool:
    if not task.next_check_at or task.status.value in {"CLOSED","CANCELLED","VERIFIED"}: return False
    now=now or datetime.now(timezone.utc); return datetime.fromisoformat(task.next_check_at)<now
def detect_coordination_loop(messages:list[dict],threshold:int=4)->bool:
    if len(messages)<threshold:return False
    recent=messages[-threshold:]; return all(not m.get("state_change") and not m.get("evidence_reference") for m in recent) and len({m.get("agent_id") for m in recent})>1
def health_recommendation(events:list[PerformanceEvent])->str:return recommendation(events)
