from __future__ import annotations

from pathlib import Path

from packages.google_workspace import DigestMessage, GWSCommandRunner, GoogleWorkspaceClient
from packages.google_workspace.command_runner import CompletedCommand


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "gws"


class FixtureExecutor:
    def __init__(self, fixture_names: list[str]) -> None:
        self.fixture_names = fixture_names
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, args, *, env, cwd, timeout):  # type: ignore[no-untyped-def]
        del env, cwd, timeout
        self.calls.append(tuple(args))
        fixture_name = self.fixture_names.pop(0)
        return CompletedCommand(
            args=tuple(args),
            returncode=0,
            stdout=(FIXTURES / fixture_name).read_text(),
            stderr="",
        )


def test_google_workspace_client_parses_recorded_gws_outputs() -> None:
    executor = FixtureExecutor(
        [
            "auth_status.out",
            "gmail_search_dry_run.out",
            "gmail_read_dry_run.out",
            "sheets_append_dry_run.out",
            "gmail_send_dry_run.out",
        ]
    )
    client = GoogleWorkspaceClient(GWSCommandRunner(executor=executor))

    auth = client.preflight()
    search = client.search_messages("label:inbox", 1, dry_run=True)
    message = client.read_message("example-message-id", dry_run=True)
    sheet = client.write_rows("sheet-id", "A1", [["a", "b"]], dry_run=True)
    send = client.send_digest(
        DigestMessage.create(to=["to@example.com"], subject="Digest", body="Body"),
        dry_run=True,
    )

    assert auth.is_usable is True
    assert search.request_preview is not None
    assert search.request_preview.method == "GET"
    assert message.subject == "Original subject"
    assert sheet.request_preview is not None
    assert sheet.request_preview.method == "POST"
    assert send.request_preview is not None
    assert send.request_preview.is_multipart_upload is True
