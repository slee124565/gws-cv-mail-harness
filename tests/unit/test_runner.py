from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from packages.config import RunConfig
from packages.google_workspace import (
    DigestMessage,
    MessageAddress,
    MessagePacket,
    MessageRef,
    RequestPreview,
    SearchMessagesResult,
    SendResult,
    SheetWriteResult,
)
from packages.runner import ProcessingRunner
from packages.state_store import SQLiteStateStore


class FakeGoogleWorkspaceClient:
    def __init__(self) -> None:
        self.search_calls = 0
        self.read_calls: list[str] = []
        self.write_dry_runs: list[bool] = []
        self.send_dry_runs: list[bool] = []
        self.sent_digests: list[DigestMessage] = []

    def search_messages(self, query: str, max_results: int) -> SearchMessagesResult:
        self.search_calls += 1
        del query, max_results
        return SearchMessagesResult(messages=(MessageRef(message_id="m-1", thread_id="t-1"),))

    def read_message(self, message_id: str) -> MessagePacket:
        self.read_calls.append(message_id)
        return MessagePacket(
            gmail_message_id=message_id,
            message_id_header=f"{message_id}@mail.example",
            thread_id="t-1",
            subject="Subject",
            sent_at="Thu, 1 Jan 2026 00:00:00 +0000",
            sender=MessageAddress(email="sender@example.com"),
            body_text="One line body",
        )

    def write_rows(self, spreadsheet_id: str, range_name: str, rows, *, dry_run: bool) -> SheetWriteResult:  # type: ignore[no-untyped-def]
        del spreadsheet_id, range_name, rows
        self.write_dry_runs.append(dry_run)
        if dry_run:
            return SheetWriteResult(
                spreadsheet_id="sheet-123",
                request_preview=RequestPreview(
                    method="POST",
                    url="https://example.test",
                ),
            )
        return SheetWriteResult(
            spreadsheet_id="sheet-123",
            updated_range="Test!A2:H2",
            updated_rows=1,
            updated_columns=8,
            updated_cells=8,
        )

    def send_digest(self, digest: DigestMessage, *, dry_run: bool) -> SendResult:
        self.send_dry_runs.append(dry_run)
        self.sent_digests.append(digest)
        if dry_run:
            return SendResult(
                request_preview=RequestPreview(
                    method="POST",
                    url="https://example.test/send",
                    is_multipart_upload=True,
                )
            )
        return SendResult(message_id="gmail-1", thread_id="thread-1")


def _config(tmp_path: Path) -> RunConfig:
    return RunConfig(
        gmail_query="label:test",
        sheet_id="sheet-123",
        sheet_range="Test!A1",
        digest_recipient="digest@example.com",
        state_db_path=tmp_path / "state.sqlite3",
    )


def test_run_once_dry_run_keeps_messages_unprocessed(tmp_path: Path) -> None:
    client = FakeGoogleWorkspaceClient()
    store = SQLiteStateStore(tmp_path / "state.sqlite3")
    runner = ProcessingRunner(client, store)

    summary = runner.run_once(_config(tmp_path), dry_run=True)

    assert summary.dry_run is True
    assert summary.processed_count == 1
    assert store.has_processed("m-1") is False
    assert client.write_dry_runs == [True]
    assert client.send_dry_runs == [True]
    assert "dry run" in client.sent_digests[0].body


def test_run_once_live_marks_processed_and_skips_rerun(tmp_path: Path) -> None:
    client = FakeGoogleWorkspaceClient()
    store = SQLiteStateStore(tmp_path / "state.sqlite3")
    runner = ProcessingRunner(client, store)
    config = replace(_config(tmp_path), dry_run_default=False)

    first_summary = runner.run_once(config)
    second_summary = runner.run_once(config)

    assert first_summary.processed_count == 1
    assert store.has_processed("m-1") is True
    assert second_summary.processed_count == 0
    assert second_summary.skipped_count == 1
    assert client.write_dry_runs == [False]
    assert client.send_dry_runs == [False, False]


def test_run_once_skips_messages_recorded_with_legacy_header_id(tmp_path: Path) -> None:
    client = FakeGoogleWorkspaceClient()
    store = SQLiteStateStore(tmp_path / "state.sqlite3")
    runner = ProcessingRunner(client, store)
    config = replace(_config(tmp_path), dry_run_default=False)

    store.create_run(
        "legacy-run",
        started_at="2026-04-17T00:00:00+00:00",
        dry_run=False,
        gmail_query=config.gmail_query,
    )
    store.mark_processed(
        "m-1@mail.example",
        run_id="legacy-run",
        processed_at="2026-04-17T00:01:00+00:00",
        thread_id="t-1",
    )
    store.finish_run(
        "legacy-run",
        finished_at="2026-04-17T00:02:00+00:00",
        matched_count=1,
        processed_count=1,
        skipped_count=0,
        failed_count=0,
        status="success",
    )

    summary = runner.run_once(config)

    assert summary.processed_count == 0
    assert summary.skipped_count == 1
