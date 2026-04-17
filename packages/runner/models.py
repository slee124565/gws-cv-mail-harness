from __future__ import annotations

from dataclasses import dataclass

from packages.google_workspace import SendResult, SheetWriteResult


@dataclass(frozen=True)
class RunItem:
    message_id: str
    thread_id: str | None
    received_at: str | None
    subject: str | None
    sender: str
    summary: str
    status: str
    processed_at: str

    def to_sheet_row(self) -> list[str]:
        return [
            self.message_id,
            self.thread_id or "",
            self.received_at or "",
            self.subject or "",
            self.sender,
            self.summary,
            self.status,
            self.processed_at,
        ]


@dataclass(frozen=True)
class RunSummary:
    run_id: str
    started_at: str
    finished_at: str
    dry_run: bool
    query: str
    matched_count: int
    processed_count: int
    skipped_count: int
    failed_count: int
    processed_items: tuple[RunItem, ...]
    skipped_message_ids: tuple[str, ...]
    failures: tuple[str, ...]
    sheet_write: SheetWriteResult | None = None
    digest_send: SendResult | None = None
