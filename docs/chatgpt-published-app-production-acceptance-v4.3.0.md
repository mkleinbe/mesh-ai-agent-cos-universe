# ChatGPT Published App Production Acceptance: v4.3.0

## Preconditions

- human-authorized v4.3.0 QNAP deployment completed;
- local QNAP verification green;
- OpenAI Secure MCP Tunnel healthy;
- production TaskLedger preserved;
- no recovery of PF-057 tasks has started;
- tests below use non-consequential work only.

## Identity and discovery

Require:

- `mcp_version=4.0.0`;
- `deployment_release=4.3.0`;
- `agent_id=cos`;
- transport `SECURE_MCP_TUNNEL` where exposed;
- exactly 10 registered agents;
- CoS catalog contains 28 agent tools;
- `delegation.execute_owner` is present;
- `approval.record_decision` and `reliability.human_override` are absent from agent tools;
- governance audit chain is valid.

## Direct-report owner-routing matrix

For each current eligible CoS direct report from the live Agent Registry:

1. create/resume a synthetic canonical child task;
2. create a canonical delegation;
3. confirm owner route is executable;
4. perform owner lifecycle transitions through `delegation.execute_owner`;
5. complete under the derived owner identity;
6. confirm CoS observes the canonical result;
7. confirm CoS is not recorded as that owner;
8. separately verify where appropriate.

Do not hard-code the matrix to CMO.

## Nested delegation

Validate using synthetic/non-consequential work:

```text
cos -> cmo -> vp-content
cos -> coo -> consultant-network-steward
```

Confirm specialist completion returns to the functional executive, executive completion returns to CoS, and identity/authority do not bleed across levels.

## Negative identity tests

Require denial for:

- caller-supplied owner/principal field;
- direct CoS completion of a child-owned task;
- child use of parent-only authority;
- cross-sibling delegated execution;
- task/delegation substitution;
- execution after owner is disabled/quarantined;
- zero-depth agent delegation;
- human-only operation through delegated owner transport.

## Scheduled execution

Execute a synthetic scheduled occurrence with deterministic intake identity. Require:

- repeated intake reuses the canonical parent;
- delegated child routes under its owner identity;
- exact owner completion retry returns the prior canonical response;
- no duplicate child/delegation/completion is produced;
- verification remains separate.

## Consequential-action boundary

Do not test owner transport by publishing, sending external messages, approving pricing, making commercial commitments, making staffing commitments, or taking another consequential external action.

Message Operations transport validation must prove approval separation without performing an unnecessary external send.

## Recovery inventory

After all transport acceptance is green, query TaskLedger for all potentially stranded work. Include at minimum:

- delegated tasks in QA awaiting owner completion;
- unresolved owner-completion/transport failures;
- delegated tasks stalled after execution;
- open dependencies caused by delegated predecessors;
- repeated retries resuming the same blocked task;
- delegated owner work lacking a completed owner route.

## PF-057 canonical task

Re-read `task-b0b613daff51` immediately before recovery. If it remains CMO-owned and in QA with the expected evidence/approval state, recover in place:

```text
existing QA
-> governed cmo owner completion
-> COMPLETED
-> separate verification where required
-> dependent gate release
```

If canonical state differs, stop and reconcile. Do not force the stale recovery sequence.

## Acceptance verdict

Production acceptance is green only when every current eligible owner route passes, both nested paths pass, scheduled execution crosses the identity boundary correctly, audit attribution is accurate, no approval/authority bypass is observed, and no consequential side effect was introduced merely for testing.
