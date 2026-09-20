# Verification v4.13.0 Slack HITL Peer Workflow

Status: IN PROGRESS until merged production promotion and final live UAT are complete.

## Automated gates

- BDD contract HITL-CHAT-001 through HITL-CHAT-015.
- Python contract and runtime drift checks.
- MCP TypeScript checks.
- Ruff and mypy.
- Full pytest with 100% mesh_cos coverage.
- Bandit high-severity gate.
- QNAP POSIX deployment regressions.
- Exact-source QNAP 4.4.0 candidate build and checksum.
- Production-equivalent container verification and MCP discovery/sequential requests.

## Live acceptance

1. Bot posts INFORMATION. Verify provider author is the approved bot and no action is requested.
2. Bot posts MANUAL_ACTION. Verify response instructions say DONE and state no approval is required.
3. Michael replies with normal language. Verify same-thread bot acknowledgment and no authority mutation.
4. Michael replies APPROVE on non-approval thread. Verify rejection as authority and explanatory acknowledgment.
5. Create synthetic PENDING L4 approval, post through post_approval, then exercise ambiguous text, APPROVE, DENY, CHANGE/CHANGES, replay, wrong-user, bot-authored, edited/unavailable, and provider-failure cases using non-consequential evidence.
6. Verify TaskLedger state and audit chain after each authority-bearing case.
7. Verify complete bot -> Michael -> dispatcher -> MCP provider reread -> bot response round trip.

## Release evidence

Repository v4.13.0 can be published only from final main SHA after all automated gates pass. Production remains unverified until the exact candidate is promoted to QNAP and Secure MCP readback plus live Slack UAT pass.
