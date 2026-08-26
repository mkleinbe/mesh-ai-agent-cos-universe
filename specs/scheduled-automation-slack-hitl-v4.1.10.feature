@ready @security-sensitive @scheduled-automation @slack-hitl
Feature: Production-hardened scheduled automation and Slack human approval
  Scheduled Mesh operating loops must use the canonical MCP lifecycle, preserve idempotency,
  deliver HITL notices only through the real OpenAI Slack bot identity, and accept approval
  authority only through a provider-authenticated human interaction boundary.

  Background:
    Given the canonical Mesh CoS MCP runtime is healthy
    And the governed Slack channel is "C0BRL4GCL3A"
    And the canonical approval entity "michael" is bound at deployment to one immutable Slack user ID for MK
    And allowed OpenAI notice authors are "U0BKV7Z8M96" and "U0BN8V2BU9Z"
    And the configured MK Slack user ID is not committed to source control
    And Slack Socket Mode is authenticated with a protected app-level token
    And the canonical approval slash command is "/mesh-approval"

  @SCH-HITL-001
  Scenario: A logical scheduled occurrence has one canonical task
    Given a Job ID and logical due timestamp form an immutable execution key
    When the dispatcher intakes that occurrence more than once
    Then it supplies the execution key as task.intake idempotency_key
    And every intake resolves the same canonical task_id
    And no duplicate canonical task is created

  @SCH-HITL-002
  Scenario: A scheduled execution follows the valid canonical lifecycle
    Given a newly intaken scheduled execution task
    When the dispatcher starts and completes the occurrence
    Then it advances through INTAKE, TRIAGED, PLANNED, ASSIGNED, IN_PROGRESS, and QA in order
    And task.complete moves QA to COMPLETED with non-empty outcome evidence
    And task.verify is a separate CoS operation from COMPLETED
    And a Sheet PASS never substitutes for canonical verification

  @SCH-HITL-003
  Scenario: HITL approval notice is authored by a real OpenAI Slack bot
    Given a canonical L4 or L5 approval request assigned to "michael"
    When an HITL approval notice is delivered
    Then provider evidence identifies the notice author as Slack user "U0BKV7Z8M96" or "U0BN8V2BU9Z"
    And the notice mentions the configured immutable Slack user ID for MK
    And the notice identifies MK or Michael as the approval owner
    And the notice contains the exact Approval ID and payload fingerprint
    And a notice authored by the configured MK user is rejected as an invalid parent notice
    And no custom bot may pass by copying an OpenAI display name

  @SCH-HITL-004
  Scenario: Slack human approval becomes canonical only through the Socket Mode slash-command boundary
    Given a pending canonical approval bound to a provider-verified OpenAI-bot-authored Slack thread
    When the runtime receives a Slack Socket Mode slash_commands envelope for "/mesh-approval"
    And the envelope carries the configured immutable MK Slack user ID
    And the command is exactly APPROVE, REJECT, or CHANGES for the bound Approval ID
    Then the non-MCP human-ingress service maps that provider interaction to principal "michael"
    And the canonical approval decision is recorded server-side
    And a fresh canonical approval read reflects the decision before consequential action
    And no agent-callable MCP tool can submit or infer that human decision

  @SCH-HITL-005
  Scenario Outline: Invalid Slack approval evidence fails closed
    Given a pending canonical approval bound to an OpenAI-bot-authored Slack thread
    When the approval evidence has <defect>
    Then no canonical human approval is recorded
    And no consequential external action is authorized

    Examples:
      | defect |
      | an ordinary Slack message attributed to MK |
      | a different Slack user ID |
      | a different channel ID |
      | a different slash command |
      | a human-authored parent notice |
      | a non-OpenAI bot parent notice |
      | an unknown Approval ID |
      | a payload fingerprint mismatch |
      | an ambiguous decision command |
      | a duplicate already-decided approval |
      | an inactive Socket Mode connection |

  @SCH-HITL-006
  Scenario: User-scoped Slack connector cannot impersonate ChatGPT or satisfy the human-interaction gate
    Given the generic Slack connector authenticates as MK
    When governed outbound HITL delivery or canonical human approval is required
    Then the connector is treated as read-only evidence for those governed boundaries
    And the workflow uses the official ChatGPT or ChatGPT Agents Slack surface for the approval notice
    And the runtime uses the authenticated Socket Mode "/mesh-approval" interaction for the human decision
    And if the bot-owned notice surface is unavailable the affected step is BLOCKED_CHATGPT_AGENT_TRANSPORT
    And the workflow never falls back to sending the HITL notice as MK
    And an ordinary connector-authored APPROVE message never becomes canonical approval

  @SCH-HITL-007
  Scenario: Production preflight validates the approval trust boundary
    When production preflight is executed with Slack HITL required
    Then it requires the governed channel ID
    And it requires a configured immutable Slack user ID for MK without committing it
    And it requires the allowed OpenAI bot user IDs
    And it requires a server-side Slack verification bot credential without exposing it
    And it requires a protected Socket Mode app-level credential
    And it requires the "/mesh-approval" command
    And it requires canonical audit integrity
    And it fails closed when any required identity, bot-notice, or human-interaction control is absent
