# v4.9.0 Verification

Required release proof:
- exactly 10 registered agents;
- no OpEx agent principal;
- one `mesh-opex-bot` external shared capability;
- COO is the sole consumer and has the matching Skill entitlement;
- request contract `mesh.opex.request.v1` and response contract `mesh.opex.handoff.v1`;
- canonical-fact mutation and external action remain false;
- CoS, CFO, AgentOps, COO, and human authority boundaries remain intact;
- package-drift and repository regression suites pass;
- v4.8.4 is historical read-only and v4.9.0 is the sole exact-SHA publisher;
- after merge, `main == tag v4.9.0 == GitHub Release target`.
