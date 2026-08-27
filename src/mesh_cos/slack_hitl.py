from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

MICHAEL_PRINCIPAL = "michael"

# Historical exact command parser retained for compatibility with archived evidence and
# lower-level tests. v4.1.17 production human approval uses _parse_thread_decision.
_DECISION_RE = re.compile(
    r"^(?P<verb>APPROVE|REJECT)\s+(?P<approval>approval-[A-Za-z0-9]+|APR-[A-Za-z0-9._:-]+)\s*$"
)
_CHANGES_RE = re.compile(
    r"^CHANGES\s+(?P<approval>approval-[A-Za-z0-9]+|APR-[A-Za-z0-9._:-]+):\s*(?P<change>\S(?:.*\S)?)\s*$"
)
_THREAD_DECISION_RE = re.compile(
    r"^(?P<verb>APPROVE|DENY|REJECT|CHANGE|CHANGES)(?::\s*(?P<change>\S(?:.*\S)?))?\s*$",
    re.IGNORECASE,
)
_SLACK_USER_ID_RE = re.compile(r"^[UW][A-Z0-9]+$")


def _configured_approver_user_id(values: Mapping[str, str]) -> str:
    direct = str(values.get("MESH_COS_SLACK_APPROVER_USER_ID", "")).strip()
    if direct:
        return direct
    identity_file = str(values.get("MESH_COS_SLACK_APPROVER_USER_ID_FILE", "")).strip()
    if not identity_file:
        return ""
    path = Path(identity_file).expanduser()
    if not path.is_file():
        raise RuntimeError("Slack approver identity file is unavailable")
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError("Slack approver identity file is empty")
    return value


@dataclass(frozen=True, slots=True)
class SlackHITLConfig:
    """Minimum Slack configuration for provider-authenticated human approval ingress.

    Slack collaboration and approval notices are handled by the connected Slack
    integration. They are informational and never create approval authority. The QNAP
    runtime needs only the governed channel, the human approver identity, and the
    separately authenticated Socket Mode event boundary.
    """

    channel_id: str
    approver_user_id: str
    approver_principal: str = MICHAEL_PRINCIPAL

    def __post_init__(self) -> None:
        if not self.channel_id.strip():
            raise RuntimeError("Slack HITL channel ID is required")
        if not _SLACK_USER_ID_RE.fullmatch(self.approver_user_id.strip()):
            raise RuntimeError("Slack HITL approver user ID must begin with U or W")
        if self.approver_principal != MICHAEL_PRINCIPAL:
            raise RuntimeError("Production HITL requires canonical principal michael")

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> SlackHITLConfig:
        values = env if env is not None else os.environ
        return cls(
            channel_id=str(values.get("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", "")).strip(),
            approver_user_id=_configured_approver_user_id(values),
            approver_principal=str(
                values.get("MESH_COS_SLACK_APPROVER_PRINCIPAL", MICHAEL_PRINCIPAL)
            ).strip(),
        )


def _parse_decision(text: str, approval_id: str) -> tuple[str, str | None]:
    """Parse the historical explicit Approval-ID command grammar."""
    match = _DECISION_RE.fullmatch(text.strip())
    if match:
        if match.group("approval") != approval_id:
            raise PermissionError("Slack decision Approval ID mismatch")
        return match.group("verb"), None
    match = _CHANGES_RE.fullmatch(text.strip())
    if match:
        if match.group("approval") != approval_id:
            raise PermissionError("Slack decision Approval ID mismatch")
        return "CHANGES", match.group("change")
    raise PermissionError("Slack decision command is not exact or attributable")


def _parse_thread_decision(text: str) -> tuple[str, str | None]:
    """Parse the v4.1.17 human thread-reply grammar.

    The Approval ID is intentionally absent from the reply. The already-bound Slack
    thread supplies routing context while provider-authenticated event identity supplies
    human attribution. Only CHANGE/CHANGES may carry free-text detail.
    """
    match = _THREAD_DECISION_RE.fullmatch(text.strip())
    if match is None:
        raise PermissionError("Slack approval reply must be APPROVE, DENY, or CHANGE")
    verb = match.group("verb").upper()
    change = match.group("change")
    if verb in {"APPROVE", "DENY", "REJECT"} and change is not None:
        raise PermissionError("Only CHANGE may include decision detail")
    if verb == "APPROVE":
        return "APPROVE", None
    if verb in {"DENY", "REJECT"}:
        return "DENY", None
    return "CHANGE", change
