# Cross-Functional Conflict Resolution

Agents are expected to disagree. Phase 1 resolves disagreement through source authority, evidence, business consequence, confidence, and reversibility rather than agent voting.

## 1. Fact authority precedes opinion

Examples:

- CFO owns financial calculations within its valid source scope.
- Revenue Intelligence owns canonical account qualification and commercial evidence where available.
- COO owns staffing/capacity feasibility.
- CMO owns marketing strategy and execution within delegated authority.
- Legal, regulatory, security, and privacy conclusions remain outside autonomous Phase 1 authority.

A cross-functional agent may challenge a fact or its interpretation, but cannot silently overwrite the authoritative source.

## 2. Domain ownership is not enterprise decision ownership

A functional agent may own a fact or recommendation without owning the enterprise tradeoff. Example:

- CFO: Option B has stronger economics.
- CRO: Option A has stronger strategic/win rationale.
- COO: Only A and C are deliverable.

CoS frames and resolves the cross-functional tradeoff only within delegated authority. Otherwise the Decision Brief goes to Michael.

## 3. No majority voting

Three agreeing agents do not automatically outweigh one authoritative source. Arbitration considers:

- authoritative source ownership
- quality and freshness of evidence
- business consequence
- confidence
- reversibility
- decision rights

## 4. Conflict record

Material disagreements create a `conflict.v1` record containing:

- conflict/task identifiers
- participants
- uncontested facts
- disputed facts
- disputed recommendations
- source authority
- business consequence
- options
- agent positions
- confidence
- reversibility
- Devil's Advocate review when required
- CoS recommendation
- reversal condition
- decision owner
- disposition

## 5. Devil's Advocate

Use Devil's Advocate for important or high-consequence recommendations when independent challenge would improve the decision. It tests assumptions, evidence gaps, second-order consequences, premortem failure modes, and reversibility. It remains advisory and cannot become the decision owner.

## 6. Escalation format

Never escalate a raw agent argument to Michael. Use a concise Decision Brief:

- Decision required
- Why now
- Known facts
- Material disagreement
- Options
- CoS recommendation
- Primary risk
- What would reverse the recommendation
- Approval/action requested

## 7. Source-of-truth conflict

If two purported authoritative sources conflict on a material decision and precedence cannot be established safely, the conflict itself is material evidence. Do not guess which source is correct. Escalate according to consequence and authority, preserving both source references.
