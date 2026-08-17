# Task Lifecycle
The state machine is enforced in code. COMPLETED means the producing agent believes execution is finished. VERIFIED requires outcome evidence and an acceptance-test pass. Verification failure returns work to REWORK or IN_PROGRESS.
