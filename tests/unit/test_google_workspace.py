from __future__ import annotations

import json
from pathlib import Path

import pytest

from packages.google_workspace import (
    DigestMessage,
    GWSCommandError,
    GWSCommandRunner,
    GoogleWorkspaceClient,
    extract_json_payload,
)
from packages.google_workspace.command_runner import CompletedCommand


class FakeExecutor:
    def __init__(self, responses: list[CompletedCommand]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, args, *, env, cwd, timeout):  # type: ignore[no-untyped-def]
        del env, cwd, timeout
        self.calls.append(tuple(args))
        if not self.responses:
            raise AssertionError("No fake response configured for command.")
        return self.responses.pop(0)


def test_extract_json_payload_ignores_noise_prefix() -> None:
    payload = extract_json_payload("Using keyring backend: keyring\n{\"token_valid\": true}")
    assert payload == {"token_valid": True}


def test_command_runner_raises_for_non_zero_exit() -> None:
    runner = GWSCommandRunner(
        executor=FakeExecutor(
            [
                CompletedCommand(
                    args=("gws", "auth", "status"),
                    returncode=2,
                    stdout="",
                    stderr="auth error",
                )
            ]
        )
    )

    with pytest.raises(GWSCommandError):
        runner.run_json(["auth", "status"])


def test_preflight_parses_auth_status() -> None:
    executor = FakeExecutor(
        [
            CompletedCommand(
                args=("gws", "auth", "status"),
                returncode=0,
                stdout=json.dumps(
                    {
                        "user": "person@example.com",
                        "auth_method": "oauth2",
                        "credential_source": "environment_variables",
                        "token_valid": True,
                        "client_config_exists": True,
                        "encrypted_credentials_exists": True,
                        "has_refresh_token": True,
                        "scope_count": 2,
                        "scopes": ["email", "openid"],
                    }
                ),
                stderr="Using keyring backend: keyring\n",
            )
        ]
    )
    client = GoogleWorkspaceClient(GWSCommandRunner(executor=executor))

    status = client.preflight()

    assert status.user == "person@example.com"
    assert status.is_usable is True
    assert executor.calls == [("gws", "auth", "status")]


def test_search_messages_builds_expected_query() -> None:
    executor = FakeExecutor(
        [
            CompletedCommand(
                args=(),
                returncode=0,
                stdout=json.dumps(
                    {
                        "dry_run": True,
                        "method": "GET",
                        "url": "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                        "query_params": [["maxResults", "5"], ["q", "label:inbox"]],
                        "body": None,
                        "is_multipart_upload": False,
                    }
                ),
                stderr="",
            )
        ]
    )
    client = GoogleWorkspaceClient(GWSCommandRunner(executor=executor))

    result = client.search_messages("label:inbox", 5, dry_run=True)

    assert result.request_preview is not None
    assert result.request_preview.url.endswith("/users/me/messages")
    command = executor.calls[0]
    assert command[:5] == ("gws", "gmail", "users", "messages", "list")
    params = json.loads(command[6])
    assert params == {"userId": "me", "maxResults": 5, "q": "label:inbox"}
    assert command[-1] == "--dry-run"


def test_read_message_parses_helper_output() -> None:
    executor = FakeExecutor(
        [
            CompletedCommand(
                args=(),
                returncode=0,
                stdout=json.dumps(
                    {
                        "thread_id": "thread-123",
                        "message_id": "message-123",
                        "from": {"email": "sender@example.com", "name": "Sender"},
                        "to": [{"email": "receiver@example.com"}],
                        "subject": "Hello",
                        "date": "Thu, 1 Jan 2026 00:00:00 +0000",
                        "body_text": "Plain body",
                        "body_html": "<p>Plain body</p>",
                    }
                ),
                stderr="",
            )
        ]
    )
    client = GoogleWorkspaceClient(GWSCommandRunner(executor=executor))

    message = client.read_message("message-123")

    assert message.gmail_message_id == "message-123"
    assert message.message_id_header == "message-123"
    assert message.sender is not None
    assert message.sender.email == "sender@example.com"
    assert message.to[0].email == "receiver@example.com"
    assert "--headers" in executor.calls[0]


def test_read_message_tolerates_list_shaped_reply_to() -> None:
    executor = FakeExecutor(
        [
            CompletedCommand(
                args=(),
                returncode=0,
                stdout=json.dumps(
                    {
                        "thread_id": "thread-123",
                        "message_id": "message-123",
                        "from": {"email": "sender@example.com"},
                        "reply_to": [],
                        "to": [{"email": "receiver@example.com"}],
                        "subject": "Hello",
                        "body_text": "Plain body",
                    }
                ),
                stderr="",
            )
        ]
    )
    client = GoogleWorkspaceClient(GWSCommandRunner(executor=executor))

    message = client.read_message("message-123")

    assert message.reply_to is None
    assert message.gmail_message_id == "message-123"


def test_write_rows_uses_configured_range() -> None:
    executor = FakeExecutor(
        [
            CompletedCommand(
                args=(),
                returncode=0,
                stdout=json.dumps(
                    {
                        "dry_run": True,
                        "method": "POST",
                        "url": "https://sheets.googleapis.com/v4/spreadsheets/sheet-123/values/Test!A1:append",
                        "query_params": [["valueInputOption", "USER_ENTERED"]],
                        "body": {"values": [["a", "b"]]},
                        "is_multipart_upload": False,
                    }
                ),
                stderr="",
            )
        ]
    )
    client = GoogleWorkspaceClient(GWSCommandRunner(executor=executor))

    result = client.write_rows("sheet-123", "Test!A1", [["a", "b"]], dry_run=True)

    assert result.request_preview is not None
    command = executor.calls[0]
    assert command[:6] == ("gws", "sheets", "spreadsheets", "values", "append", "--params")
    params = json.loads(command[6])
    assert params["spreadsheetId"] == "sheet-123"
    assert params["range"] == "Test!A1"
    body = json.loads(command[8])
    assert body == {"values": [["a", "b"]]}


def test_send_digest_builds_expected_flags() -> None:
    executor = FakeExecutor(
        [
            CompletedCommand(
                args=(),
                returncode=0,
                stdout=json.dumps(
                    {
                        "dry_run": True,
                        "method": "POST",
                        "url": "https://gmail.googleapis.com/upload/gmail/v1/users/me/messages/send",
                        "query_params": [],
                        "body": None,
                        "is_multipart_upload": True,
                    }
                ),
                stderr="",
            )
        ]
    )
    client = GoogleWorkspaceClient(GWSCommandRunner(executor=executor))

    digest = DigestMessage.create(
        to=["to@example.com"],
        cc=["cc@example.com"],
        bcc=["bcc@example.com"],
        from_email="alias@example.com",
        subject="Digest",
        body="Body",
        attachments=[str(Path("report.txt"))],
    )
    result = client.send_digest(digest, dry_run=True, draft=True)

    assert result.request_preview is not None
    command = executor.calls[0]
    assert "--to" in command
    assert "--cc" in command
    assert "--bcc" in command
    assert "--from" in command
    assert "--attach" in command
    assert command[-2:] == ("--dry-run", "--draft")
