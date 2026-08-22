from datetime import datetime,timezone,timedelta
from mesh_cos.answer_desk import decide
from mesh_cos.authority import classify
from mesh_cos.models import AuthorityLevel,TaskRecord,TaskStatus
from mesh_cos.conflict import authoritative_owner,decision_brief
from mesh_cos.staffing import readiness
from mesh_cos.performance import PerformanceEvent,recommendation
from mesh_cos.slack import SlackEventGuard
from mesh_cos.agentops import detect_coordination_loop
from mesh_cos.lifecycle import transition

def test_01_team_question():assert decide(known_fact=True,source_accessible=True,established_policy=False,reversible=True,requires_judgment=False,ceo_authority=False,requester_permissions=set()).disposition=='ANSWERED'
def test_02_pricing():assert classify('pricing').human_approval_required
def test_03_conflict():
    assert authoritative_owner('financial_calculation')=='cfo';b=decision_brief(decision_required='select option',why_now='proposal due',known_facts=['CFO margin calc'],material_disagreement='CRO favors strategic value',options=['A','B'],cos_recommendation='A',primary_risk='margin',reversal_condition='economics worsen',approval_requested='approve');assert b['cos_recommendation']=='A'
def test_04_infeasible_staffing():assert readiness(capability_match=False,availability_checked_at=None,max_age_days=30,rate_valid=True,contracting_ready=True,availability_confirmed=False)=='NOT_A_FIT'
def test_05_stale():
    old=(datetime.now(timezone.utc)-timedelta(days=31)).isoformat();assert readiness(capability_match=True,availability_checked_at=old,max_age_days=30,rate_valid=True,contracting_ready=True,availability_confirmed=True)=='REQUIRES_REFRESH'
def test_06_publication_gate():assert classify('public_publish').required_level==AuthorityLevel.L4
def test_07_watch():assert recommendation([PerformanceEvent('x',str(i),'first_pass_quality',.4) for i in range(5)])=='WATCH'
def test_08_quarantine():assert recommendation([PerformanceEvent('x','T','evidence_governance',0,'CRITICAL')])=='QUARANTINE'
def test_09_duplicate():
    g=SlackEventGuard();assert g.accept('1') and not g.accept('1')
def test_10_loop():assert detect_coordination_loop([{'agent_id':'a'},{'agent_id':'b'},{'agent_id':'a'},{'agent_id':'b'}])
def test_11_missing_source():assert authoritative_owner('enterprise_cash_balance') is None
def test_12_low_confidence():assert classify('internal_recommendation',AuthorityLevel.L3,material=True,low_confidence=True).human_approval_required
def test_13_verification_rework():
    t=TaskRecord(task_id='T',objective='o',expected_outcome='e',requested_by='m',executive_sponsor='m',accountable_agent='cro',decision_owner='m',acceptance_test='verify')
    t.outcome='done';t.outcome_evidence=['evidence://completion']
    for s in [TaskStatus.TRIAGED,TaskStatus.PLANNED,TaskStatus.ASSIGNED,TaskStatus.IN_PROGRESS,TaskStatus.QA,TaskStatus.COMPLETED]:transition(t,s)
    transition(t,TaskStatus.REWORK);assert t.status==TaskStatus.REWORK and t.rework_count==1
