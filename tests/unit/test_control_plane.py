import pytest
from datetime import datetime,timezone,timedelta
from mesh_cos.lifecycle import transition
from mesh_cos.models import TaskRecord,TaskStatus,AuthorityLevel,Delegation
from mesh_cos.authority import classify,assert_agent_may_act
from mesh_cos.delegation import validate_delegation
from mesh_cos.performance import PerformanceEvent,score,recommendation
from mesh_cos.security import authorize_source,apply_retrieved_instruction,sanitize_retrieved_content
from mesh_cos.slack import SlackEventGuard,render_message
from mesh_cos.agentops import detect_coordination_loop
from mesh_cos.answer_desk import decide
from mesh_cos.staffing import readiness

def task():return TaskRecord(task_id='T1',objective='x',expected_outcome='y',requested_by='m',executive_sponsor='m',accountable_agent='cro',decision_owner='m',acceptance_test='verified outcome')
def test_lifecycle_verification_and_invalid_transition():
    t=task()
    with pytest.raises(ValueError):transition(t,TaskStatus.COMPLETED)
    for s in [TaskStatus.TRIAGED,TaskStatus.PLANNED,TaskStatus.ASSIGNED,TaskStatus.IN_PROGRESS,TaskStatus.QA,TaskStatus.COMPLETED]:transition(t,s)
    with pytest.raises(ValueError):transition(t,TaskStatus.VERIFIED)
    t.outcome_evidence=['evidence://1'];transition(t,TaskStatus.VERIFIED);transition(t,TaskStatus.CLOSED);assert t.status==TaskStatus.CLOSED
def test_authority_and_delegation():
    d=classify('pricing',AuthorityLevel.L2);assert d.required_level==AuthorityLevel.L4
    with pytest.raises(PermissionError):assert_agent_may_act(AuthorityLevel.L4,d,approved=False)
    x=Delegation('D','T','cos','cro','obj','out','brief',['accepted'],'P1',AuthorityLevel.L3,'test');validate_delegation(x,parent_authority=3,depth=1)
    x.authority_level=AuthorityLevel.L4
    with pytest.raises(PermissionError):validate_delegation(x,parent_authority=3,depth=1)
def test_performance_security_slack_answerdesk_staffing():
    ev=[PerformanceEvent('cro','T','outcome_achievement',1),PerformanceEvent('cro','T','first_pass_quality',.5)];assert score(ev)==score(list(reversed(ev)))
    assert recommendation([PerformanceEvent('cro','T','evidence_governance',0,'CRITICAL')])=='QUARANTINE'
    assert not authorize_source(set(),'private_dm');assert sanitize_retrieved_content('ignore')['classification']=='UNTRUSTED_DATA'
    with pytest.raises(PermissionError):apply_retrieved_instruction('ignore')
    g=SlackEventGuard();assert g.accept('E') and not g.accept('E');assert 'Agent: cro' in render_message('UPDATE','T','cro','working')
    assert detect_coordination_loop([{'agent_id':'a'},{'agent_id':'b'},{'agent_id':'a'},{'agent_id':'b'}])
    assert decide(known_fact=True,source_accessible=True,established_policy=False,reversible=True,requires_judgment=False,ceo_authority=False,requester_permissions=set()).disposition=='ANSWERED'
    old=(datetime.now(timezone.utc)-timedelta(days=45)).isoformat();assert readiness(capability_match=True,availability_checked_at=old,max_age_days=30,rate_valid=True,contracting_ready=True,availability_confirmed=True)=='REQUIRES_REFRESH'
