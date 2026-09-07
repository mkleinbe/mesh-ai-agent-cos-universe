# v4.7.0 Enterprise Consulting Skill Security Review

Date: 2026-09-07  
Applicability: `FULL_REVIEW`

## Scope

This release changes agent role guidance for consumption of external and composed Skills. It does not change the machine-readable agent registry, MCP tool surface, source permissions, credentials, database schema, delegation depth, decision authority, or production deployment.

## Trust boundaries reviewed

- donor repository concepts versus Mesh authority;
- PPMD method outputs versus canonical functional truth;
- Revenue Intelligence stakeholder evidence versus unsupported buyer inference;
- decision memo structure versus decision approval;
- meeting/workshop artifacts versus commitments;
- critic QA versus design and publication authority;
- completion versus verification;
- Skill capability versus agent authority;
- internal artifacts versus external communication execution.

## Threats and controls

| Threat | Control |
|---|---|
| Donor prompt or instruction contamination | Donor concepts are method input only; canonical Mesh source, evidence, privacy, approval, and L0-L5 controls dominate |
| Skill capability interpreted as agent authority | Agent guidance and regression explicitly state capability is not authority; registry remains unchanged |
| Hypothesis treated as fact | Day-1 hypothesis remains falsifiable and evidence-linked; functional truth owners remain authoritative |
| Confirmation bias | Disconfirming tests, branch/whole kill criteria, low-conviction exposure, and reversal conditions |
| Stakeholder intent fabrication | Revenue Intelligence v1.4+ evidence-bound state; unsupported fields remain `unknown`; no personality, politics, hidden-intent, advocacy, budget, or purchase-intent inference |
| Memo self-approval | Explicit authority/approval state; recommendation and yes/no ask do not authorize execution |
| Meeting/workshop commitment creep | Existing owner and L0-L5 approval controls remain authoritative |
| Design-authority bypass | Critic output is QA input only; Mesh Design System / Artifact Designer retain authority |
| Autonomous communication | Message Operations and human approval remain separate; no send/publish tool or new binding added |
| Completion-verification collapse | CoS guidance and tests preserve `COMPLETED` distinct from `VERIFIED` |
| Sensitive-data expansion | No new source, connector, credential, persistence, or data field introduced |

## Registry review

The canonical `agents/registry.json` is intentionally unchanged by v4.7.0. The release preserves:

- exactly 10 agents;
- canonical parentage;
- direct Skill arrays;
- shared-capability set;
- decision-authority strings;
- prohibited actions;
- required approvals;
- delegation depths;
- tool allowlists and external-action boundaries.

## Donor supply-chain review

The released Skill repositories record `sruthir28/enterprise-ai-skills` at commit `ae8fe60a765cc766e0c598bfe8a7a33fd5faac1b` under MIT. Agent guidance does not import donor files or instructions. Donor branding, McKinsey branding, persuasion mechanics, politics labeling, individual-contributor AI scoring, unsupported stakeholder psychology, false precision, and authority-bypass mechanics are not adopted.

## Findings

No critical or high security finding is accepted for this agent-integration release. The agent repository adds no third-party package, executable donor code, network path, secret, connector scope, or consequential action.

Codex Security scan evidence is unavailable in this runtime and is not claimed. Independent evidence consists of exact-tree review plus the repository's full CI, 100% branch-aware Python coverage gate, Bandit gate, TypeScript/MCP checks, runtime/package drift checks, action-surface checks, and the v4.7.0 governance regressions.

## Residual risk

Model adherence remains probabilistic. Residual risk is bounded by explicit negative guidance, unchanged machine-readable registry authority, functional source ownership, human approval, Message Operations separation, and independent verification before release.
