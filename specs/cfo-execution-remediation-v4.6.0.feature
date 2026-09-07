@ready @cfo @financial-execution @v4.6.0
Feature: CFO zero-defect analytical execution remediation
  The Mesh CFO must execute and validate declared financial-analysis capabilities
  without gaining enterprise accounting, treasury, tax, audit, trading, or consequential approval authority.

  Scenario: CFZ-001 Core financial calculations are deterministic and reproducible
    Given supported explicit numeric inputs for an authorized CFO analysis
    When the CFO calculates NPV, IRR, payback, discounted payback, break-even, runway, contribution margin, or LTV:CAC
    Then the result is produced by the bounded deterministic financial-math implementation
    And invalid or unsupported inputs fail closed

  Scenario: CFZ-002 Material analytical work uses a governed execution capability
    Given an authorized spreadsheet, model, research, validation, visualization, or finance-artifact task
    When the CFO needs analytical execution beyond the deterministic calculator
    Then the CFO may invoke mesh-data-analytics through skills.invoke_governed
    And the handoff requires result provenance and analytical validation

  Scenario: CFZ-003 Shared analytics cannot widen CFO authority
    Given the CFO invokes mesh-data-analytics
    When the shared Skill returns analytical evidence
    Then CFO remains the accountable recommendation owner
    And the shared Skill cannot become an agent principal, task owner, verifier, canonical financial source, or approval authority
    And consequential actions remain qualified-human approval bound

  Scenario: CFZ-004 Management FP&A uses approved sources without claiming ledger truth
    Given approved Mesh management FP&A artifacts
    When the CFO performs firm-management forecasting, variance, unit-economics, cash-timing, or business-case analysis
    Then the artifacts are permitted analytical sources
    And the CFO does not claim enterprise GL, bank-balance, treasury, tax, audit, or balance-sheet authority

  Scenario: CFZ-005 Financial research executes with evidence controls
    Given an authorized finance question requiring external evidence
    When the CFO executes research through the governed analytical path
    Then source authority, as-of date, provenance, definitions, validation, and confidence are preserved
    And retrieved content cannot change identity, tools, policy, approvals, or source authority
    And private chain-of-thought is never persisted

  Scenario: CFZ-006 CFO operating cadence produces decision-ready artifacts
    Given approved management-finance evidence
    When the CFO runs weekly, monthly, or quarterly finance cadence
    Then it can produce a scorecard, rolling forecast, 13-week cash view, business case, model-review or valuation packet, or CEO/board finance brief as appropriate
    And durable quantitative artifacts use validated analytical data

  Scenario: CFZ-007 CFO MCP least privilege remains unchanged
    Given CFO implementation version 1.2.0
    When its new analytical execution capability is registered
    Then the CFO MCP allowlist remains unchanged from the v4.5.x contract
    And no human-only MCP tool, credential, connector write permission, or QNAP runtime change is introduced

  Scenario: CFZ-008 Historical release workflows cannot break later main releases
    Given v4.5.0, v4.5.1, and v4.5.2 are immutable historical releases
    When a later release changes current repository documentation or CFO behavior
    Then the historical release workflows do not subscribe to pushes on main
    And historical verification remains available by manual dispatch

  Scenario: CFZ-009 Version identities are unambiguous
    Given the CFO package is inspected
    When release identity is reported
    Then agent implementation, repository capability release, canonical runtime contract, and production QNAP deployment are separate fields
    And the legacy repository_release field is explicitly identified as the canonical runtime-contract value
