@ready @qnap @slack @hitl @v4_1_17
Feature: Bot-authored provider-authenticated Slack HITL for human approval and change requests
  Mesh uses the dedicated ChatGPT Enterprise AI Agent Slack app for all governed approval collaboration. The bot renders Block Kit controls, Slack supplies the authenticated human interaction boundary, and TaskLedger remains canonical for approval, change, and replay state.

  Rule: Approval threads are routing context, not authority
    @QNAP-116 @priority-critical @happy-path
    Scenario: Bot-posted approval notice binds a Slack thread to one pending approval
      Given a canonical TaskLedger approval is PENDING for principal michael with an immutable payload fingerprint
      When the QNAP runtime posts the approval through the dedicated Slack bot with chat.postMessage
      Then Slack returns the provider channel and root message timestamp
      And the runtime binds that Slack thread to the exact pending Approval ID and canonical payload fingerprint
      And the approval remains PENDING
      And message authorship does not become approval authority

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
        | reply                    | disposition |
        | APPROVE                  | APPROVE     |
        | approve                  | APPROVE     |
        | DeNy                     | DENY        |
        | change                   | CHANGE      |

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

  Rule: Slash commands and ChatGPT connector impersonation are not part of the production contract
    @QNAP-120 @priority-critical @architecture
    Scenario: QNAP stages the Slack HITL runtime
      Given Slack HITL is required
      When v4.1.17 production preflight validates Slack configuration
      Then it requires the governed approver identity, an xapp Socket Mode app token, and an xoxb bot token
      And it does not require or validate a /mesh-approval slash command
      And the bot token is used without username or icon overrides
      And the ChatGPT connected Slack plugin is not the execution path for governed Slack approval messages

  Rule: Slack provider unavailability remains fail-closed for consequential approval
    @QNAP-121 @priority-critical @resilience
    Scenario: Slack Socket Mode interaction ingress is unavailable
      Given Slack HITL is required
      And the QNAP container cannot maintain Slack Socket Mode connectivity
      When the MCP process remains otherwise healthy
      Then the MCP HTTP service remains running
      And readiness reports Slack HITL as unavailable
      And pending consequential approvals remain blocked
      And the Socket Mode listener retries with bounded backoff without terminating the process

  Rule: Approval notices use Block Kit and the dedicated bot identity
    @QNAP-122 @priority-critical @ux @security
    Scenario: CoS requests a governed Slack approval notice
      Given a canonical PENDING approval exists with an immutable payload fingerprint
      When CoS invokes slack-adapter to post that approval
      Then the server calls Slack chat.postMessage with the protected bot token
      And the message is authored by the configured Slack app identity rather than MK
      And the message includes rich_text content plus Approve, Deny, and Change buttons
      And the root message timestamp returned by Slack is stored as the canonical approval-thread binding
      And no incoming-webhook URL or ChatGPT connector handoff is required

  Rule: Block Kit buttons are provider-authenticated human decisions
    @QNAP-123 @priority-critical @happy-path
    Scenario Outline: MK clicks an approval action button
      Given a bot-authored Block Kit approval message is bound to a PENDING approval owned by michael
      When Slack delivers a block_actions Socket Mode envelope from the configured MK user with <button>
      Then the runtime maps the button to <disposition>
      And the exact bound approval and payload fingerprint are used server-side
      And no Approval ID supplied by free text is trusted for routing

      Examples:
        | button  | disposition |
        | Approve | APPROVE     |
        | Deny    | DENY        |
        | Change  | CHANGE      |

  Rule: Change is a conversation, not a brittle one-line decision
    @QNAP-124 @priority-critical @ux
    Scenario: MK clicks Change
      Given a bot-authored approval message is bound to a PENDING approval owned by michael
      When Slack delivers the provider-authenticated Change button action from MK
      Then the approval remains PENDING
      And the runtime records an AWAITING_CHANGE_INPUT state bound to that approval and thread
      And the bot replies in the same thread with What would you like to change?
      And no consequential action is authorized

    @QNAP-125 @priority-critical @happy-path
    Scenario: MK supplies freeform change instructions
      Given the bound approval is AWAITING_CHANGE_INPUT
      When Slack delivers the next provider-authenticated human message from MK in that thread
      Then the full freeform instruction is stored as a governed change request
      And the original approval is rejected as superseded by requested changes
      And the task returns to IN_PROGRESS for intelligent revision
      And no external action is executed from the freeform instruction itself

    @QNAP-126 @priority-critical @orchestration
    Scenario: CoS processes a governed change request
      Given a captured change request is pending agent revision
      When the accountable CoS workflow resumes the task
      Then it uses the change instruction as untrusted human-authored requirements input
      And it revises the requested artifact, action, target, or channel as appropriate to the task
      And it requests a new approval with a new immutable payload fingerprint before any consequential action
      And the dedicated Slack bot posts the revised approval as a fresh Block Kit approval request

  Rule: Slack app configuration supports the exact private-channel interaction surface
    @QNAP-127 @priority-critical @configuration
    Scenario: Production Slack app manifest is validated
      Given mesh-agent-ops is a private Slack channel
      Then the bot has chat:write and groups:history scopes
      And event subscriptions include message.groups for freeform thread replies
      And Socket Mode is enabled for Events API and Block Kit interactions
      And interactivity is enabled
      And the bot display name is ChatGPT Enterprise AI Agent
      And the app-level token retains connections:write

  Rule: Exposed incoming-webhook URLs are never committed or used as primary authority infrastructure
    @QNAP-128 @priority-high @security
    Scenario: v4.1.17 packages Slack runtime configuration
      Then no Slack incoming-webhook URL is present in source, configuration, logs, release metadata, or TaskLedger
      And bot-token chat.postMessage is the canonical outbound approval path
      And webhook rotation is an operator security action outside the release bundle
