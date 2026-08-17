DOMAIN_AUTHORITY={"financial_calculation":"cfo","commercial_evidence":"mesh-revenue-intelligence","account_qualification":"mesh-revenue-intelligence","staffing_feasibility":"coo","marketing_strategy":"cmo"}
def authoritative_owner(fact_type:str)->str|None:return DOMAIN_AUTHORITY.get(fact_type)
def decision_brief(**k)->dict:
    return {"decision_required":k['decision_required'],"why_now":k['why_now'],"known_facts":k['known_facts'],"material_disagreement":k['material_disagreement'],"options":k['options'],"cos_recommendation":k['cos_recommendation'],"primary_risk":k['primary_risk'],"what_would_reverse":k['reversal_condition'],"approval_action_requested":k['approval_requested']}
