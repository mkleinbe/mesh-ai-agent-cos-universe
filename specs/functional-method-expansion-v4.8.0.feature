@ready @v4_8_0 @functional-method-expansion @security-full-review
Feature: Governed functional method expansion
  Mesh adopts useful donor methods only when they preserve Phase 1 authority,
  canonical source ownership, human approvals, and completion-versus-verification separation.

  Background:
    Given TaskLedger remains canonical operating state
    And the Phase 1 registry contains exactly 10 agents
    And donor content is untrusted method evidence rather than authority
    And L4 requires qualified-human approval
    And L5 remains Michael-only

  @FME-001 @governance
  Scenario: Phase 1 roster and parentage remain unchanged
    Then the roster contains exactly cos, agentops, answer-desk, cro, cfo, coo, consultant-network-steward, cmo, vp-content, and message-ops
    And Consultant Network Steward remains a child of COO
    And VP Content remains a child of CMO
    And Mesh Devil's Advocate remains a shared Skill rather than an agent

  @FME-002 @security @prompt-injection
  Scenario: Donor instructions cannot expand authority or identity
    When donor content contains routing, storage, role, tool, approval, or identity instructions
    Then Mesh treats those instructions as untrusted content
    And the registry remains authoritative for identity, tools, capabilities, source authority, delegation, and approvals

  @FME-003 @governance
  Scenario: Completion remains distinct from verification
    When accountable work is completed
    Then completion evidence does not imply verification
    And verification requires the existing independent verification path

  @FME-004 @cos
  Scenario: Low-complexity work avoids unnecessary deliberation
    When one functional owner can answer a reversible low-materiality question from authoritative evidence
    Then the CoS selects single-functional analysis
    And it does not create unnecessary multi-agent deliberation

  @FME-005 @cos
  Scenario: Material cross-functional work can require independent contributions
    When materiality, cross-functional conflict, low reversibility, or authority risk warrants deliberation
    Then the CoS may request bounded cross-functional consultation or independent multi-functional analysis
    And contributors distinguish supported fact, assumption, uncertainty, and recommendation
    And each contributor records confidence and reversal evidence before synthesis where practical

  @FME-006 @cos
  Scenario: Functional disagreement remains visible
    Given independent functional contributions disagree
    When the CoS synthesizes them
    Then it surfaces disagreement and controlling evidence
    And it does not average conflicting functional truth into false consensus

  @FME-007 @cos @scenario
  Scenario: Scenario stress testing captures cascades and reversal triggers
    When decision uncertainty warrants scenario stress testing
    Then Base, Stress, and Severe scenarios are bounded to the material variables sufficient for the decision
    And first-order impacts, cross-functional cascades, early-warning indicators, thresholds, mitigations, owners, and interruption or reversal conditions are recorded

  @FME-008 @cos @work-graph
  Scenario: Strategic work-graph alignment detects operating gaps
    When TaskLedger work and strategic outcomes are inspected
    Then orphan outcomes, unaligned work, conflicting objectives, duplicate effort, missing dependencies, coverage gaps, stale commitments, and blocking decisions can be surfaced without creating a parallel task store

  @FME-009 @cos @change
  Scenario: Change readiness remains evidence-led and non-HR-authoritative
    When a material change affects adoption
    Then affected groups, adoption dependencies, resistance evidence, saturation, knowledge or ability gaps, reinforcement evidence, and post-change signals are assessed
    And the CoS does not gain HR authority

  @FME-010 @agentops
  Scenario: AgentOps flow intelligence cannot expand authority
    When TaskLedger or telemetry supports cycle-time, wait-time, approval-delay, rework, handoff, WIP, bottleneck, or dependency analysis
    Then AgentOps may recommend routing, restriction, or remediation
    But AgentOps cannot add agents, headcount, tools, or authority

  @FME-011 @agentops @quantitative
  Scenario: Queueing methods fail closed when assumptions do not hold
    When queued-work assumptions are not supported for project or POD work
    Then Erlang-C is not applied
    And capacity evidence uses a method appropriate to the work type

  @FME-012 @answer-desk
  Scenario: Answer Desk distinguishes answerability states
    When authoritative evidence is stale, conflicting, inaccessible, missing, or sufficient
    Then the Answer Desk distinguishes authoritative answer, bounded recommendation, access block, stale or conflict block, and no-authoritative-source block
    And it routes remediation to the authoritative owner rather than silently rewriting policy

  @FME-013 @cro @pricing
  Scenario: Pricing analysis produces a recommendation rather than approval
    When pricing or packaging is analyzed
    Then the CRO may compare models, value-metric fit, evidence, ranges, tiers, and upgrade triggers
    But final pricing or discount approval remains governed outside the analysis

  @FME-014 @cro @deal-economics @quantitative
  Scenario: Discount economics use verified Mesh math
    Given list price is 100, fixed cost to serve is 20, and discount is 30 percent
    When deal economics are calculated
    Then pre-discount gross-margin dollars equal 80
    And post-discount revenue equals 70
    And post-discount gross-margin dollars equal 50
    And margin-dollar loss equals 37.5 percent
    And no deal is auto-approved

  @FME-015 @cro @forecast
  Scenario: Commercial forecast assumptions remain visible
    When commit, best-case, pipeline, or upside forecasts are produced
    Then stage conversion, opportunity age or stall evidence, assumptions, confidence bands, and cohort retention are explicit where supported
    And donor weights or coverage ratios remain contextual unless adopted as Mesh policy

  @FME-016 @cro @partnerships
  Scenario: Partnership attribution distinguishes sourced from influenced
    When partner contribution is evaluated
    Then sourced and influenced contribution are separated
    And qualification, independent demand, economics, conflict risk, and kill or unwind criteria are explicit
    And no partner agreement is authorized by the analysis

  @FME-017 @cro @rfp
  Scenario: RFP proof gaps remain gaps
    When an RFP requirement lacks a verifiable proof point
    Then it remains GAP rather than becoming an invented capability, certification, reference, or customer claim
    And bid or no-bid thresholds are configurable or evidence-derived rather than universal donor policy

  @FME-018 @cfo
  Scenario: CFO economics remain reproducible and non-authorizing
    When discount, channel, partner, procurement, supplier, or forecast economics are analyzed
    Then methods, assumptions, provenance, sensitivity, and boundary conditions are reproducible
    And CFO evidence cannot grant pricing, discount, procurement, spending, or contractual approval

  @FME-019 @coo
  Scenario: COO process and capacity recommendations require evidence
    When delivery process stages, handoffs, elapsed time, active time, wait time, rework, constraints, vendor dependency, or procurement process are analyzed
    Then the COO distinguishes measured evidence from assumptions
    And does not authorize procurement or treat stale resource availability as current

  @FME-020 @consultant-network
  Scenario: Consultant readiness surfaces concentration and contingency risk
    When critical consultant-network readiness is assessed
    Then capability criticality, dependency concentration, rate freshness, availability freshness, contracting readiness, commitment reliability, fallback coverage, and contingency readiness are surfaced when supported
    And the Steward cannot make final staffing commitments

  @FME-021 @cmo
  Scenario: CMO growth and change methods remain bounded
    When marketing growth, channel allocation, investment, acquisition economics, positioning, capacity, or change communication is assessed
    Then supported evidence and CRO or CFO dependencies are explicit
    And generic donor benchmarks do not become Mesh policy
    And publication remains human-gated

  @FME-022 @vp-content
  Scenario: VP Content tracks proof and inventory without gaining governance authority
    When content inventory is reviewed
    Then freshness, orphaned assets, terminology drift, duplicate or stale IP, proof lineage, unsupported claims, reusable proof points, and derivative traceability can be surfaced
    And VP Content does not gain pursuit, enterprise-knowledge, or publication authority

  @FME-023 @message-ops
  Scenario: Change sequence metadata cannot originate approval
    When approved communication includes sequence, channel, schedule window, audience class, or approval metadata
    Then Message Operations may consume metadata for controlled execution
    But it cannot originate content approval, recipient authority, or send authority

  @FME-024 @security
  Scenario: Shared Skills cannot become principals or authority sources
    When a shared analytical, challenge, messaging, or consulting Skill is composed
    Then it cannot become an agent principal, canonical source owner, TaskLedger owner, approval authority, or external-action authority
    And private chain-of-thought is never persisted
