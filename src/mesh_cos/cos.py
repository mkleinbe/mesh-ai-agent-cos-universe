from .authority import classify
from .models import AuthorityLevel
def route_work(domain:str)->str:return {"commercial":"cro","finance":"cfo","delivery":"coo","marketing":"cmo","team_question":"answer-desk","agent_health":"agentops","external_message":"message-ops","challenge":"devils-advocate"}.get(domain,"cos")
def should_escalate(action:str,*,requested_level:AuthorityLevel,material:bool=False,reversible:bool=True,external:bool=False,low_confidence:bool=False)->bool:return classify(action,requested_level,material=material,reversible=reversible,external=external,low_confidence=low_confidence).human_approval_required
