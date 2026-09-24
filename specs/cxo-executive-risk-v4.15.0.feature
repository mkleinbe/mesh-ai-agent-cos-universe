@ready
Feature: CxO Executive Risk Routing v4.15.0

  Scenario: CXR2-001 CRO routes margin risk to CFO
    Given CRO identifies a material margin risk
    When the shared executive-risk router classifies the category
    Then the risk is handed to CFO without transferring risk-acceptance authority

  Scenario: CXR2-002 CFO routes staffing risk to COO
    Given CFO identifies a staffing-dependency risk
    When the shared executive-risk router classifies the category
    Then the risk is handed to COO without transferring risk-acceptance authority

  Scenario: CXR2-003 COO routes unsupported public claim risk to CMO
    Given COO identifies an unsupported public claim risk
    When the shared executive-risk router classifies the category
    Then the risk is handed to CMO without transferring publication authority

  Scenario: CXR2-004 CMO routes pricing precedent risk to CRO
    Given CMO identifies a pricing-precedent risk
    When the shared executive-risk router classifies the category
    Then the risk is handed to CRO and economic evidence remains with CFO when needed

  Scenario: CXR2-005 consequential risk acceptance is human
    Given any CxO Skill produces a material risk record
    When the v2 record is created
    Then the acceptance principal is a qualified human role and never the Skill

  Scenario: CXR2-006 unknown delivery capacity does not block early pursuit
    Given delivery capacity is unknown
    And no concrete staffing or timeline commitment is required
    When the capacity gate is evaluated
    Then early pursuit continues and no capacity decision is required

  Scenario: CXR2-007 concrete delivery commitment requires a human capacity decision
    Given concrete delivery-need evidence exists
    And a staffing or timeline commitment is being considered
    When the capacity gate is evaluated
    Then a qualified human owns the capacity decision

  Scenario: CXR2-008 manageable risk does not become a generic veto
    Given a material risk affects one dependent action
    And independent reversible work remains
    When risk routing runs
    Then independent work continues and only the dependent action is staged

  Scenario: CXR2-009 executive-risk v1 remains readable
    Given a historical mesh.executive-risk.v1 record
    When deterministic validation runs
    Then the record remains valid for backward-compatible intake

  Scenario: CXR2-010 executive-risk v2 requires source lineage
    Given a new mesh.executive-risk.v2 record
    When deterministic validation runs
    Then source lineage and a qualified-human acceptance role are required
