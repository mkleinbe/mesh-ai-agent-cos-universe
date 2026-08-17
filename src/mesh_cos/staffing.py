from datetime import datetime,timezone
def readiness(*,capability_match:bool,availability_checked_at:str|None,max_age_days:int,rate_valid:bool,contracting_ready:bool,availability_confirmed:bool)->str:
    if not capability_match:return "NOT_A_FIT"
    if not availability_checked_at:return "REQUIRES_REFRESH"
    if (datetime.now(timezone.utc)-datetime.fromisoformat(availability_checked_at)).days>max_age_days or not availability_confirmed:return "REQUIRES_REFRESH"
    if not rate_valid or not contracting_ready:return "NOT_READY"
    return "STAFFING_READY"
