Feature: Commercial Growth OS agent integration
  The existing Phase 1 agents consume the Commercial Growth OS without gaining new authority.

  Scenario: Commercial checkpoint uses human business state
    Given a scheduled or triggered commercial checkpoint
    When the Chief of Staff reports the result
    Then it leads with BUSINESS_PROGRESS, RESPONSIBLE_NO_ACTION, BUSINESS_FAILURE, or SYSTEM_FAILURE

  Scenario: CRO uses the existing GTM front door
    Given a commercial motion needs orchestration
    When CRO routes work
    Then mesh-gtm-orchestrator remains the commercial family front door
    And Revenue Intelligence remains canonical commercial truth

  Scenario: Product independence preserves advisory authority
    Given partner economics are attractive
    When CRO evaluates a product route
    Then partner economics do not increase technical fit
    And Strategy and Cyber can recommend a better non-partner option

  Scenario: Partner economics remain CFO-owned
    Given a partner route is commercially relevant
    When economics are analyzed
    Then CFO owns supported economics
    And economics are separated from architecture fit

  Scenario: Partner delivery feasibility remains COO-owned
    Given a partner-assisted pursuit may require implementation capacity
    When feasibility is evaluated
    Then COO owns current delivery and partner-capacity evidence

  Scenario: Phase 1 roster is unchanged
    Given the Commercial Growth OS is integrated
    When the agent registry is validated
    Then exactly 10 Phase 1 agents remain registered
    And no new commercial principal agent exists
