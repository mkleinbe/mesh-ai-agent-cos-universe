from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest

import mesh_cos.slack_bot as slack_bot

CHANNEL = "C0BRL4GCL3A"
ROOT = "1787866770.386509"
MESSAGE = "1787866782.586999"


class _Response:
    def __init__(self, body: dict[str, Any]) -> None:
        self.body = json.dumps(body).encode("utf-8")

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        return False

    def read(self, limit: int) -> bytes:
        assert limit == 1_000_001
        return self.body


def test_conversations_replies_uses_get_query_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[Any] = []

    def urlopen(request: Any, timeout: int) -> _Response:
        captured.append(request)
        assert timeout == 10
        return _Response({"ok": True, "messages": []})

    monkeypatch.setattr(slack_bot.urllib.request, "urlopen", urlopen)
    result = slack_bot._default_transport(
        "conversations.replies",
        {
            "channel": CHANNEL,
            "ts": ROOT,
            "oldest": MESSAGE,
            "latest": MESSAGE,
            "inclusive": True,
            "limit": 1,
        },
        "xoxb-test",
    )

    assert result == {"ok": True, "messages": []}
    request = captured[0]
    assert request.get_method() == "GET"
    assert request.data is None
    parsed = urlparse(request.full_url)
    assert parsed.path.endswith("/conversations.replies")
    assert parse_qs(parsed.query) == {
        "channel": [CHANNEL],
        "ts": [ROOT],
        "oldest": [MESSAGE],
        "latest": [MESSAGE],
        "inclusive": ["true"],
        "limit": ["1"],
    }
    assert request.get_header("Authorization") == "Bearer xoxb-test"
    assert "xoxb-test" not in request.full_url


def test_conversations_history_uses_get_for_deployment_scope_probe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[Any] = []

    def urlopen(request: Any, timeout: int) -> _Response:
        captured.append(request)
        return _Response({"ok": True, "messages": []})

    monkeypatch.setattr(slack_bot.urllib.request, "urlopen", urlopen)
    slack_bot._default_transport(
        "conversations.history",
        {"channel": CHANNEL, "limit": 1},
        "xoxb-test",
    )
    request = captured[0]
    assert request.get_method() == "GET"
    assert parse_qs(urlparse(request.full_url).query) == {
        "channel": [CHANNEL],
        "limit": ["1"],
    }


def test_chat_write_transport_remains_post_json(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[Any] = []

    def urlopen(request: Any, timeout: int) -> _Response:
        captured.append(request)
        return _Response({"ok": True, "channel": CHANNEL, "ts": ROOT})

    monkeypatch.setattr(slack_bot.urllib.request, "urlopen", urlopen)
    slack_bot._default_transport(
        "chat.postMessage",
        {"channel": CHANNEL, "text": "approval"},
        "xoxb-test",
    )
    request = captured[0]
    assert request.get_method() == "POST"
    assert json.loads(request.data.decode("utf-8")) == {
        "channel": CHANNEL,
        "text": "approval",
    }
    assert request.get_header("Content-type") == "application/json; charset=utf-8"


def test_slack_provider_error_code_is_preserved_without_response_detail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        slack_bot.urllib.request,
        "urlopen",
        lambda request, timeout: _Response(
            {
                "ok": False,
                "error": "missing_scope",
                "response_metadata": {"messages": ["sensitive provider detail"]},
            }
        ),
    )
    with pytest.raises(RuntimeError) as caught:
        slack_bot._default_transport(
            "conversations.replies",
            {"channel": CHANNEL, "ts": ROOT},
            "xoxb-test",
        )
    assert str(caught.value) == "Slack Web API rejected the request: missing_scope"
    assert "sensitive provider detail" not in str(caught.value)


def test_slack_provider_error_is_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        slack_bot.urllib.request,
        "urlopen",
        lambda request, timeout: _Response({"ok": False, "error": "<unsafe-detail>"}),
    )
    with pytest.raises(RuntimeError, match="unknown_error"):
        slack_bot._default_transport(
            "conversations.replies",
            {"channel": CHANNEL, "ts": ROOT},
            "xoxb-test",
        )
