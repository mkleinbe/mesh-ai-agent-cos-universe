# Slack Agent Collaboration Protocol
Slack is an observable collaboration layer. Canonical state lives in the ledger. One task maps to one thread. Structured types: ASSIGN, ACK, UPDATE, REQUEST, EVIDENCE, RISK, BLOCKED, CONFLICT, RECOMMEND, DECISION, APPROVAL, COMPLETE, VERIFY. No thinking aloud or social filler. Duplicate event IDs are ignored. Repeated agent exchanges without state change or evidence are flagged as coordination loops.

Channel IDs and bot credentials are configuration only. No personal Slack IDs are hardcoded.
