from __future__ import annotations

from pathlib import Path

from packages.state_store import SQLiteStateStore


def test_state_store_tracks_processed_messages_and_runs(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite3"
    store = SQLiteStateStore(database_path)

    store.create_run("run-1", started_at="2026-04-17T00:00:00+00:00", dry_run=True, gmail_query="q")
    assert store.has_processed("message-1") is False

    store.mark_processed(
        "message-1",
        run_id="run-1",
        processed_at="2026-04-17T00:01:00+00:00",
        thread_id="thread-1",
    )
    store.record_digest(
        "run-1",
        recipient="digest@example.com",
        status="dry_run_preview",
        sent_at="2026-04-17T00:02:00+00:00",
        draft_id="draft-1",
    )
    store.finish_run(
        "run-1",
        finished_at="2026-04-17T00:03:00+00:00",
        matched_count=1,
        processed_count=1,
        skipped_count=0,
        failed_count=0,
        status="success",
    )

    runs = store.list_runs()
    processed = store.list_processed_messages()
    digest = store.get_digest("run-1")

    assert store.has_processed("message-1") is True
    assert runs[0].processed_count == 1
    assert processed[0].thread_id == "thread-1"
    assert digest is not None
    assert digest.draft_id == "draft-1"
