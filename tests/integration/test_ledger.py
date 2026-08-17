from mesh_cos.ledger import TaskLedger
from mesh_cos.models import TaskRecord
from mesh_cos.audit import AuditEvent
def test_task_and_event_are_canonical_and_idempotent():
    l=TaskLedger();t=TaskRecord(task_id='T',objective='o',expected_outcome='e',requested_by='m',executive_sponsor='m',accountable_agent='cro',decision_owner='m',acceptance_test='a')
    l.save_task(t);assert l.get_task('T').accountable_agent=='cro'
    e=AuditEvent('created','cos','T',t.correlation_id,0,'ok',idempotency_key='same').to_dict();assert l.record_event(e);assert not l.record_event(e)
