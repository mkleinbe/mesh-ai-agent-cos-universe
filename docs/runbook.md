# Runbook
1. Set configuration from `.env.example`.
2. Keep the kill switch enabled until integration credentials and approval owners are validated.
3. Configure private agent-ops and Answer Desk Slack channel IDs.
4. Run contract and evaluation tests before enabling routing changes.
5. On critical defect, stop automated actions, quarantine the agent, preserve audit evidence, and review authorization/provenance before restoring service.
