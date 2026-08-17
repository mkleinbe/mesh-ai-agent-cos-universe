from dataclasses import dataclass,field
MESSAGE_TYPES={"ASSIGN","ACK","UPDATE","REQUEST","EVIDENCE","RISK","BLOCKED","CONFLICT","RECOMMEND","DECISION","APPROVAL","COMPLETE","VERIFY"}
@dataclass(slots=True)
class SlackEventGuard:
    seen_event_ids:set[str]=field(default_factory=set)
    def accept(self,event_id:str)->bool:
        if event_id in self.seen_event_ids:return False
        self.seen_event_ids.add(event_id);return True
def render_message(kind:str,task_id:str,agent_id:str,action:str,evidence_reference:str|None=None,requested_next_action:str|None=None)->str:
    if kind not in MESSAGE_TYPES:raise ValueError("Unknown structured Slack message type")
    lines=[f"[{kind}] {task_id}",f"Agent: {agent_id}",f"Action: {action}"]
    if evidence_reference:lines.append(f"Evidence: {evidence_reference}")
    if requested_next_action:lines.append(f"Next: {requested_next_action}")
    return "\n".join(lines)
