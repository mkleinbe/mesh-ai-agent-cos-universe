@ready @slack @hitl @v4_2_0 @security
Feature: ChatGPT native Slack event-triggered human approval
  ChatGPT-native Slack message events wake one Mesh Slack HITL Dispatcher task. The trigger is routing only. Mesh CoS MCP re-reads Slack provider state and canonical TaskLedger state before recording any human approval authority.

  Rule: The native Slack task trigger is never an authority assertion
    @SLACK-NATIVE-001 @priority-critical
    Scenario: MK replies in a bound approval thread
      Given a PENDING approval owned by michael is bound to a bot-authored Slack root message and immutable payload fingerprint
      When a ChatGPT native Slack new-message trigger wakes the Mesh Slack HITL Dispatcher
      Then the dispatcher supplies only the governed channel ID, root thread timestamp, and reply message timestamp to Mesh CoS MCP
      And it does not supply decision text, approval status, actor, principal, or an approval boolean
      And TaskLedger remains unchanged until server-side reconciliation succeeds

  Rule: Provider state is re-derived server-side
    @SLACK-NATIVE-002 @priority-critical @happy-path
    Scenario Outline: Exact provider-authenticated MK reply records the intended decision
      Given the dispatcher provides a bound thread timestamp and message timestamp
      When the QNAP runtime retrieves the exact reply from Slack conversations.replies
      And Slack attributes the unedited manual reply to U01KG3CNYHK in C0BRL4GCL3A
      And the canonical approval is still PENDING for michael with the bound immutable payload fingerprint
      And the provider message contains <reply>
      Then the runtime records <disposition> for canonical principal michael
      And the audit record states CHATGPT_NATIVE_SLACK_EVENT_TRIGGER_RECONCILIATION
      And the trigger itself is recorded as non-authoritative

      Examples:
        | reply   | disposition |
        | APPROVE | APPROVE     |
        | approve | APPROVE     |
        | DENY    | DENY        |
        | CHANGE  | CHANGE      |

  Rule: Trigger spoofing and stale provider state fail closed
    @SLACK-NATIVE-003 @priority-critical @security
    Scenario Outline: Non-authoritative or non-reconcilable interaction is rejected
      Given a native Slack trigger wakes the dispatcher
      When server-side reconciliation observes <condition>
      Then the approval remains PENDING
      And no consequential authority is granted

      Examples:
        | condition |
        | a different Slack user |
        | an app-authored or bot-authored message |
        | another channel |
        | an unbound thread |
        | a root message instead of a reply |
        | an edited message |
        | a deleted or no-longer-retrievable message |
        | more than one exact provider result |
        | an unrecognized decision word |
        | a changed canonical payload fingerprint |
        | an already decided approval with a different provider message |

  Rule: Native-trigger replay is idempotent
    @SLACK-NATIVE-004 @priority-critical @security
    Scenario: ChatGPT delivers the same new-message trigger more than once
      Given one Slack reply has already been reconciled using its channel and message timestamp
      When the dispatcher repeats reconciliation for the same provider message
      Then the runtime returns the previously recorded canonical result idempotently
      And no second approval decision is created

  Rule: Change remains a two-step governed conversation
    @SLACK-NATIVE-005 @priority-critical
    Scenario: MK requests a change and supplies freeform requirements
      Given a bound approval is PENDING
      When MK replies CHANGE and the native trigger is reconciled
      Then the approval remains PENDING in AWAITING_CHANGE_INPUT
      And the bot asks what should change in the same thread
      When MK sends the next new manual human reply in that thread
      And the native trigger is independently reconciled
      Then the full provider-retrieved text is stored as untrusted change requirements
      And the old approval is superseded
      And the task returns to IN_PROGRESS
      And a new approval with a new payload fingerprint is required before consequential action

  Rule: QNAP no longer owns Slack event ingress
    @SLACK-NATIVE-006 @priority-critical @architecture
    Scenario: v4.2.0 production runtime starts
      Then no Slack Socket Mode app token is required or mounted
      And no QNAP Slack WebSocket listener is required for readiness
      And Secure MCP Tunnel remains the remote MCP ingress
      And the dedicated Slack bot token remains protected for bot-authored notices and server-side provider reconciliation
      And the 10-agent workforce and 27-tool public MCP catalog remain unchanged

  Rule: Approval notices advertise only supported interaction
    @SLACK-NATIVE-007 @priority-high @ux
    Scenario: CoS posts a governed approval request
      Then the dedicated bot posts the approval summary and immutable bound thread
      And the notice instructs MK to reply APPROVE, DENY, or CHANGE
      And it does not expose non-functional approval buttons

  Rule: Native task provisioning is externally acceptance-tested
    @SLACK-NATIVE-008 @priority-critical @deployment
    Scenario: Production acceptance exercises the ChatGPT-native trigger
      Given one Mesh Slack HITL Dispatcher task is configured for new messages in C0BRL4GCL3A from U01KG3CNYHK
      When MK sends a synthetic reply in a bound non-consequential approval thread
      Then the dispatcher runs once or idempotently repeats
      And MCP provider reconciliation updates the synthetic canonical approval
      And no scheduled polling loop or QNAP Socket Mode listener is used
