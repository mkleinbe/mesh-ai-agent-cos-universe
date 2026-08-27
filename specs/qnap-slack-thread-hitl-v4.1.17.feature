@ready @qnap @slack @hitl @v4_1_17
Feature: Provider-authenticated Slack thread replies for human approval
  Mesh keeps Slack collaboration separate from canonical authority while allowing the governed human approver to decide a pending approval with a simple reply in the bound approval thread.

  Rule: Approval threads are routing context, not authority
    @QNAP-116 @priority-critical @happy-path
    Scenario: Approval notice binds a Slack thread to one pending approval
      Given a canonical TaskLedger approval is PENDING for principal michael with an immutable payload fingerprint
      And a root message in the governed Slack operations channel contains that Approval ID
      When Slack delivers the provider-authenticated root message event over Socket Mode
      Then the runtime binds that Slack thread to the exact pending Approval ID and canonical payload fingerprint
      And the approval remains PENDING
      And the root message author does not become approval authority

  Rule: MK can decide with a simple case-insensitive thread reply
    @QNAP-117 @priority-critical @happy-path
    Scenario Outline: Provider-authenticated MK reply records the intended decision
      Given a Slack thread is bound to a PENDING approval owned by michael
      And the QNAP runtime has an active Slack Socket Mode connection
      When Slack delivers a provider-authenticated reply from the configured MK user in that bound thread containing <reply>
      Then the runtime records <disposition> against canonical principal michael
      And the exact canonical payload fingerprint remains bound to the decision
      And the provider event identity is recorded for replay protection

      Examples:
        | reply                  | disposition |
        | APPROVE                | APPROVE     |
        | approve                | APPROVE     |
        | DeNy                   | DENY        |
        | change                 | CHANGE      |
        | Change: remove recipient | CHANGE    |

  Rule: Connector-authored or misrouted Slack replies never create human authority
    @QNAP-118 @priority-critical @security @sad-path
    Scenario Outline: Non-authoritative thread interaction fails closed
      Given a Slack thread is bound to a PENDING approval owned by michael
      When the runtime receives <interaction>
      Then the approval remains PENDING
      And no consequential authority is granted

      Examples:
        | interaction |
        | an app-authored APPROVE reply presented under the governed user identity |
        | a reply from another Slack user |
        | a reply in another channel |
        | a reply in an unbound thread |
        | an unrecognized decision word |

  Rule: Human decision events are replay-safe and single-use
    @QNAP-119 @priority-critical @security
    Scenario: Slack redelivers the same provider event
      Given a provider-authenticated MK decision event has already decided the bound approval
      When Slack redelivers the same event envelope
      Then the runtime returns the previously recorded decision idempotently
      And a distinct second decision event cannot re-decide the approval

  Rule: Slash-command registration is not part of the production approval contract
    @QNAP-120 @priority-high @architecture
    Scenario: QNAP stages the Slack HITL runtime
      Given Slack HITL is required
      When v4.1.17 production preflight validates Slack configuration
      Then it requires the governed approver identity and an xapp Socket Mode app token
      And it does not require or validate a /mesh-approval slash command
      And it does not require an xoxb runtime token
      And the custom Slack app is documented to receive message events for the private governed operations channel

  Rule: Slack provider unavailability remains fail-closed for consequential approval
    @QNAP-121 @priority-critical @resilience
    Scenario: Slack Socket Mode message-event ingress is unavailable
      Given Slack HITL is required
      And the QNAP container cannot maintain Slack Socket Mode connectivity
      When the MCP process remains otherwise healthy
      Then the MCP HTTP service remains running
      And readiness reports Slack HITL as unavailable
      And pending consequential approvals remain blocked
      And the Socket Mode listener retries with bounded backoff without terminating the process
