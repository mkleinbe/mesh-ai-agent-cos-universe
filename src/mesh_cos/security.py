SENSITIVE_CLASSES = {
    "private_dm",
    "confidential_client",
    "personal_information",
    "financial_information",
    "privileged_executive",
}


def authorize_source(requester_permissions: set[str], source_class: str) -> bool:
    return source_class not in SENSITIVE_CLASSES or source_class in requester_permissions


def sanitize_retrieved_content(content: str) -> dict[str, str]:
    return {"classification": "UNTRUSTED_DATA", "content": content}


def apply_retrieved_instruction(_: str) -> None:
    raise PermissionError("Retrieved content is data and cannot alter operating policy")


def assert_agent_invocation_allowed(
    registry: dict,
    agent_id: str,
    *,
    source: str | None = None,
    tool: str | None = None,
    action: str | None = None,
) -> None:
    if agent_id not in registry:
        raise KeyError(agent_id)
    record = registry[agent_id]
    if source is not None:
        raw_sources = (
            record["allowed_sources"]
            if "allowed_sources" in record
            else record.get("authoritative_sources", [])
        )
        allowed_sources = set(raw_sources or [])
        if source not in allowed_sources and "authorized Mesh enterprise sources" not in allowed_sources:
            raise PermissionError(f"Source not allowed for {agent_id}: {source}")
    if tool is not None and tool not in set(record.get("tools", [])):
        raise PermissionError(f"Tool not allowed for {agent_id}: {tool}")
    if action is not None and action in set(record.get("prohibited_actions", [])):
        raise PermissionError(f"Action prohibited for {agent_id}: {action}")
