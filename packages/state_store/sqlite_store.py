from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    started_at: str
    finished_at: str | None
    dry_run: bool
    gmail_query: str
    matched_count: int
    processed_count: int
    skipped_count: int
    failed_count: int
    status: str
    notes: str | None


@dataclass(frozen=True)
class ProcessedMessageRecord:
    message_id: str
    thread_id: str | None
    run_id: str
    processed_at: str


@dataclass(frozen=True)
class DigestRecord:
    run_id: str
    recipient: str
    status: str
    sent_at: str
    message_id: str | None
    draft_id: str | None


class SQLiteStateStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    dry_run INTEGER NOT NULL,
                    gmail_query TEXT NOT NULL,
                    matched_count INTEGER NOT NULL DEFAULT 0,
                    processed_count INTEGER NOT NULL DEFAULT 0,
                    skipped_count INTEGER NOT NULL DEFAULT 0,
                    failed_count INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL,
                    notes TEXT
                );

                CREATE TABLE IF NOT EXISTS processed_messages (
                    message_id TEXT PRIMARY KEY,
                    thread_id TEXT,
                    run_id TEXT NOT NULL,
                    processed_at TEXT NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                );

                CREATE TABLE IF NOT EXISTS digest_events (
                    run_id TEXT PRIMARY KEY,
                    recipient TEXT NOT NULL,
                    status TEXT NOT NULL,
                    sent_at TEXT NOT NULL,
                    message_id TEXT,
                    draft_id TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                );
                """
            )

    def create_run(self, run_id: str, *, started_at: str, dry_run: bool, gmail_query: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO runs (run_id, started_at, dry_run, gmail_query, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, started_at, int(dry_run), gmail_query, "running"),
            )

    def finish_run(
        self,
        run_id: str,
        *,
        finished_at: str,
        matched_count: int,
        processed_count: int,
        skipped_count: int,
        failed_count: int,
        status: str,
        notes: str | None = None,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE runs
                SET finished_at = ?,
                    matched_count = ?,
                    processed_count = ?,
                    skipped_count = ?,
                    failed_count = ?,
                    status = ?,
                    notes = ?
                WHERE run_id = ?
                """,
                (
                    finished_at,
                    matched_count,
                    processed_count,
                    skipped_count,
                    failed_count,
                    status,
                    notes,
                    run_id,
                ),
            )

    def has_processed(self, message_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM processed_messages WHERE message_id = ?",
                (message_id,),
            ).fetchone()
        return row is not None

    def mark_processed(
        self,
        message_id: str,
        *,
        run_id: str,
        processed_at: str,
        thread_id: str | None = None,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO processed_messages (message_id, thread_id, run_id, processed_at)
                VALUES (?, ?, ?, ?)
                """,
                (message_id, thread_id, run_id, processed_at),
            )

    def record_digest(
        self,
        run_id: str,
        *,
        recipient: str,
        status: str,
        sent_at: str,
        message_id: str | None = None,
        draft_id: str | None = None,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO digest_events (run_id, recipient, status, sent_at, message_id, draft_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (run_id, recipient, status, sent_at, message_id, draft_id),
            )

    def list_runs(self, *, limit: int = 10) -> list[RunRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT run_id, started_at, finished_at, dry_run, gmail_query,
                       matched_count, processed_count, skipped_count, failed_count, status, notes
                FROM runs
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            RunRecord(
                run_id=row["run_id"],
                started_at=row["started_at"],
                finished_at=row["finished_at"],
                dry_run=bool(row["dry_run"]),
                gmail_query=row["gmail_query"],
                matched_count=row["matched_count"],
                processed_count=row["processed_count"],
                skipped_count=row["skipped_count"],
                failed_count=row["failed_count"],
                status=row["status"],
                notes=row["notes"],
            )
            for row in rows
        ]

    def list_processed_messages(self, *, limit: int = 20) -> list[ProcessedMessageRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT message_id, thread_id, run_id, processed_at
                FROM processed_messages
                ORDER BY processed_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            ProcessedMessageRecord(
                message_id=row["message_id"],
                thread_id=row["thread_id"],
                run_id=row["run_id"],
                processed_at=row["processed_at"],
            )
            for row in rows
        ]

    def get_digest(self, run_id: str) -> DigestRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT run_id, recipient, status, sent_at, message_id, draft_id
                FROM digest_events
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return DigestRecord(
            run_id=row["run_id"],
            recipient=row["recipient"],
            status=row["status"],
            sent_at=row["sent_at"],
            message_id=row["message_id"],
            draft_id=row["draft_id"],
        )
