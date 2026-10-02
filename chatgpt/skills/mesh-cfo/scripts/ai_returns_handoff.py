"""Bound an existing Skill's consumption to a host-verified specialist result."""
from copy import deepcopy
import hashlib
import json
import re

SPECIALISTS={'mesh-ai-outcome-measurement','mesh-ai-investment-economics','mesh-ai-value-attribution',
             'mesh-ai-benefits-realization','mesh-ai-value-assurance'}
REQUIRED={'owner_skill','client_id','assessment_id','value_contract_id','source_digest','result','external_action','new_agent'}


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def consume(result,expected,owner):
    """The host verifies provenance and permissions before supplying expected, not the source document."""
    if not isinstance(result,dict) or set(result)!=REQUIRED: raise ValueError('Malformed specialist result')
    if result['owner_skill'] not in SPECIALISTS or result['external_action'] is not False or result['new_agent'] is not False:
        raise ValueError('Unexpected specialist authority')
    needed={'client_id','assessment_id','value_contract_id','source_digest','result_digest','execution_receipt_ref'}
    if not isinstance(expected,dict) or set(expected)!=needed: raise ValueError('Host verification binding is required')
    if not isinstance(result['result'],dict): raise ValueError('Specialist result must be an object')
    for key in ('client_id','assessment_id','value_contract_id'):
        if not isinstance(result[key],str) or not result[key].strip(): raise ValueError('Client and assessment identities must be nonempty strings')
        if not isinstance(expected[key],str) or not expected[key].strip(): raise ValueError('Invalid host identity')
    for value in (result['source_digest'],expected['source_digest'],expected['result_digest']):
        if not isinstance(value,str) or re.fullmatch('[a-f0-9]{64}',value) is None: raise ValueError('Invalid evidence digest')
    if not isinstance(expected['execution_receipt_ref'],str) or not expected['execution_receipt_ref'].strip(): raise ValueError('Invalid host execution receipt')
    for key in ('client_id','assessment_id','value_contract_id','source_digest'):
        if result[key]!=expected[key]: raise ValueError('Cross-client or stale specialist result')
    if canonical_hash(result)!=expected['result_digest'] or not expected['execution_receipt_ref']:
        raise ValueError('Specialist execution receipt is missing or does not match')
    if not isinstance(owner,str) or not owner.startswith('mesh-'): raise ValueError('Existing owner Skill is required')
    return {'owner_skill':owner,'value_contract_id':result['value_contract_id'],'client_id':result['client_id'],
            'assessment_id':result['assessment_id'],'specialist_result':deepcopy(result),
            'execution_receipt_ref':expected['execution_receipt_ref'],'commercial_truth_owner':'mesh-revenue-intelligence',
            'external_action':False,'new_agent':False,'human_approval_created':False}
