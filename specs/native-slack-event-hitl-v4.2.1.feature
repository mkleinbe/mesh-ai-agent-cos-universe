@ready @slack @hitl @v4_2_1 @security
Feature: ChatGPT native Slack event-triggered human approval patch
  v4.2.1 preserves the v4.2.0 locator-only ChatGPT Work dispatcher and server-side Slack provider reconciliation while accepting Slack's observed whole-message bold representation of an otherwise exact human decision token.

  Rule: The ChatGPT Work dispatcher remains non-authoritative
    @SLACK-NATIVE-421-001 @priority-critical
    Scenario: MK replies in a bound approval thread
      Given a PENDING approval owned by michael is bound to a bot-authored Slack root message and immutable payload fingerprint
      When a ChatGPT native Slack new-message trigger wakes the Mesh Slack HITL Dispatcher
      Then the dispatcher supplies only the governed channel ID, root thread timestamp, and reply message timestamp to Mesh CoS MCP
      And it does not supply message text, decision, approval status, actor, principal, user ID, or an approval boolean
      And TaskLedger remains unchanged until server-side reconciliation succeeds

  Rule: Provider-rendered exact decision tokens remain exact decisions
    @SLACK-NATIVE-421-002 @priority-critical @happy-path
    Scenario Outline: Provider-authenticated MK reply records the intended decision
      Given the dispatcher provides a bound thread timestamp and message timestamp
      When the QNAP runtime retrieves the exact reply from Slack conversations.replies
      And Slack attributes the unedited manual reply to U01KG3CNYHK in C0BRL4GCL3A
      And the canonical approval is still PENDING for michael with the bound immutable payload fingerprint
      And the provider message text is <reply>
      Then the runtime records <disposition> for canonical principal michael
      And the audit record states CHATGPT_NATIVE_SLACK_EVENT_TRIGGER_RECONCILIATION
      And the trigger itself is recorded as non-authoritative

      Examples:
        | reply       | disposition |
        | APPROVE     | APPROVE     |
        | approve     | APPROVE     |
        | *APPROVE*   | APPROVE     |
        | DENY        | DENY        |
        | *DENY*      | DENY        |
        | CHANGE      | CHANGE      |
        | *CHANGE*    | CHANGE      |

  Rule: Formatting compatibility is narrow and fail closed
    @SLACK-NATIVE-421-003 @priority-critical @security
    Scenario Outline: Non-exact formatted text cannot create approval authority
      Given a native Slack trigger wakes the dispatcher for a bound thread reply
      When server-side provider reconciliation reads <reply>
      Then the approval remains PENDING
      And no consequential authority is granted

      Examples:
        | reply                 |
        | **APPROVE**           |
        | *APPROVE* extra       |
        | *looks good*          |
        | please APPROVE        |
        | APPROVE: because yes  |

  Rule: Existing identity and state controls remain authoritative
    @SLACK-NATIVE-421-004 @priority-critical @security
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
        | a changed canonical payload fingerprint |
        | an already decided approval with a different provider message |

  Rule: Native-trigger replay remains idempotent
    @SLACK-NATIVE-421-005 @priority-critical @security
    Scenario: ChatGPT delivers the same new-message trigger more than once
      Given one Slack reply has already been reconciled using its channel and message timestamp
      When the dispatcher repeats reconciliation for the same provider message
      Then the runtime returns the previously recorded canonical result idempotently
      And no second approval decision is created

  Rule: Change remains a two-step governed conversation
    @SLACK-NATIVE-421-006 @priority-critical
    Scenario: MK requests a change and supplies freeform requirements
      Given a bound approval is PENDING
      When MK replies CHANGE or *CHANGE* and the native trigger is reconciled
      Then the approval remains PENDING in AWAITING_CHANGE_INPUT
      And the bot asks what should change in the same thread
      When MK sends the next new manual human reply in that thread
      And the native trigger is independently reconciled
      Then the full provider-retrieved text is stored as untrusted change requirements
      And the old approval is superseded
      And the task returns to IN_PROGRESS
      And a new approval with a new payload fingerprint is required before consequential action

  Rule: v4.2.1 remains ChatGPT-native and Socket Mode free
    @SLACK-NATIVE-421-007 @priority-critical @architecture
    Scenario: v4.2.1 production runtime starts
      Then no Slack Socket Mode app token is required or mounted
      And no QNAP Slack WebSocket listener is required for readiness
      And Secure MCP Tunnel remains the remote MCP ingress
      And the dedicated Slack bot token remains protected for bot-authored notices and server-side provider reconciliation
      And the 10-agent workforce and 27-tool public MCP catalog remain unchanged

  Rule: Production acceptance reproduces the v4.2.0 incident shape
    @SLACK-NATIVE-421-008 @priority-critical @deployment
    Scenario: Live acceptance uses a Slack-rendered bold approval reply
      Given one Mesh Slack HITL Dispatcher task is configured for new messages in C0BRL4GCL3A from U01KG3CNYHK
      And a synthetic non-consequential approval is bound to a Slack thread
      When MK replies with a message whose Slack provider text is *APPROVE*
      Then the dispatcher fires through the ChatGPT-native event path
      And MCP provider reconciliation records APPROVED exactly once
      And the task becomes READY_FOR_ACTION
      And the audit chain remains valid
