@ready @qnap @slack @hitl @v4_1_15
Feature: Slack plugin collaboration with narrow authenticated human approval ingress
  Mesh uses the connected Slack plugin for collaboration and notification while preserving a separate provider-authenticated human approval boundary for consequential actions.

  Rule: Slack collaboration does not create approval authority
    @QNAP-104 @priority-high @happy-path
    Scenario: Connected Slack plugin carries the approval request
      Given a canonical TaskLedger approval is PENDING for principal michael
      When the approval request is sent to the governed Slack operations channel through the connected Slack integration
      Then no Slack bot-authored notice verification is required
      And no verifier bot token is required by the QNAP runtime
      And the TaskLedger approval remains PENDING until authenticated human ingress records a decision

  Rule: Only provider-authenticated slash commands can decide an approval
    @QNAP-105 @priority-critical @happy-path
    Scenario: MK approves through the Mesh approval slash command
      Given a canonical TaskLedger approval is PENDING for principal michael with an immutable payload fingerprint
      And the QNAP runtime has an active Slack Socket Mode connection
      When Slack delivers a slash_commands envelope for /mesh-approval from the configured MK user in the governed channel
      Then the approval decision is recorded against canonical principal michael
      And the provider envelope identity is recorded for replay protection
      And the exact payload fingerprint remains bound to the approval

    @QNAP-106 @priority-critical @sad-path
    Scenario Outline: Non-authoritative Slack interaction cannot approve
      Given a canonical TaskLedger approval is PENDING for principal michael
      When the runtime receives <interaction>
      Then the approval remains PENDING
      And no consequential authority is granted

      Examples:
        | interaction |
        | an ordinary Slack message containing APPROVE |
        | a slash command from another Slack user |
        | a slash command from another channel |
        | a replayed or conflicting Socket Mode envelope |

  Rule: Slack provider unavailability does not crash the MCP runtime
    @QNAP-107 @priority-critical @resilience
    Scenario: Socket Mode cannot connect during MCP startup
      Given Slack HITL is required
      And the QNAP container cannot reach Slack over HTTPS or WSS
      When the MCP process starts
      Then the MCP HTTP service remains running
      And readiness reports Slack HITL as unavailable
      And consequential actions remain fail-closed
      And the Socket Mode listener retries with bounded backoff without terminating the process

  Rule: QNAP deployment uses only the minimum Slack secret
    @QNAP-108 @priority-high @security
    Scenario: Upgrade from v4.1.14 preserves only the Socket Mode app token
      Given an existing QNAP deployment contains Slack approver identity, verifier token, and Socket Mode app token files
      When v4.1.15 is staged
      Then the runtime requires the configured approver identity and Socket Mode app token
      And it does not mount, validate, prompt for, or depend on a Slack verifier bot token
      And it does not log any protected Slack credential value
