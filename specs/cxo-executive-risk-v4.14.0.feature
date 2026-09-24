@ready
Feature: CxO Executive Risk Management v4.14.0

  Scenario: CXR-001 CRO owns commercial-risk recommendation
    Given a material commercial risk is identified
    When CRO evaluates the decision
    Then CRO may recommend treatment within commercial remit
    And consequential risk acceptance remains human

  Scenario: CXR-002 CFO owns supported economic-risk recommendation
    Given a material margin or economic risk is identified
    When CFO evaluates the decision
    Then CFO preserves supported financial evidence and assumptions
    And CFO does not gain treasury tax audit or unrestricted finance authority

  Scenario: CXR-003 COO capacity becomes relevant only with concrete delivery need
    Given delivery capacity is unknown
    And no concrete staffing or delivery commitment is required
    When COO risk analysis is composed with an early pursuit
    Then unknown capacity does not become an early commercial blocker

  Scenario: CXR-004 CMO owns marketing and reputation risk recommendation
    Given a material brand audience or public-narrative risk is identified
    When CMO evaluates it
    Then CMO may recommend treatment within marketing remit
    And CMO does not gain publication authority

  Scenario: CXR-005 CRO routes margin uncertainty to CFO
    Given CRO identifies material margin uncertainty
    When cross-functional risk routing runs
    Then CFO receives the economic-risk handoff

  Scenario: CXR-006 CFO routes staffing constraint to COO
    Given CFO identifies a staffing feasibility constraint
    When cross-functional risk routing runs
    Then COO receives the operational-risk handoff

  Scenario: CXR-007 COO routes public claim risk to CMO
    Given COO identifies a reputational or public-claim concern
    When cross-functional risk routing runs
    Then CMO receives the marketing-risk handoff

  Scenario: CXR-008 CMO routes pricing exposure to CRO and CFO
    Given CMO identifies material pricing exposure
    When cross-functional risk routing runs
    Then CRO and CFO receive the commercial and economic handoff

  Scenario: CXR-009 shared risk contract preserves owner and acceptance owner
    Given a cross-functional risk is handed off
    When mesh.executive-risk.v1 is used
    Then treatment ownership and risk-acceptance ownership remain explicit

  Scenario: CXR-010 manageable risk does not block independent reversible work
    Given risk affects one dependent consequential action
    When independent reversible work remains
    Then unaffected work continues
