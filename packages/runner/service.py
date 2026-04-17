from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from packages.config import RunConfig
from packages.digest import build_digest
from packages.google_workspace import GoogleWorkspaceClient
from packages.runner.models import RunItem, RunSummary
from packages.state_store import SQLiteStateStore


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _summarize_body(body_text: str | None) -> str:
    if not body_text:
        return "(no body)"
    collapsed = " ".join(part for part in body_text.splitlines() if part.strip())
    return collapsed[:157] + "..." if len(collapsed) > 160 else collapsed


class ProcessingRunner:
    def __init__(self, client: GoogleWorkspaceClient, state_store: SQLiteStateStore) -> None:
        self.client = client
        self.state_store = state_store

    def run_once(self, config: RunConfig, *, dry_run: bool | None = None) -> RunSummary:
        effective_dry_run = config.dry_run_default if dry_run is None else dry_run
        run_id = uuid4().hex
        started_at = _utc_now()
        self.state_store.create_run(
            run_id,
            started_at=started_at,
            dry_run=effective_dry_run,
            gmail_query=config.gmail_query,
        )

        processed_items: list[RunItem] = []
        skipped_message_ids: list[str] = []
        failures: list[str] = []
        sheet_result = None
        digest_result = None

        status = "success"
        notes: str | None = None
        try:
            search_result = self.client.search_messages(config.gmail_query, config.max_results)
            for reference in search_result.messages:
                if self.state_store.has_processed(reference.message_id):
                    skipped_message_ids.append(reference.message_id)
                    continue

                try:
                    message = self.client.read_message(reference.message_id)
                except Exception as exc:  # pragma: no cover - covered by runner tests via fake client
                    failures.append(f"{reference.message_id}: {exc}")
                    continue

                if (
                    message.message_id_header
                    and self.state_store.has_processed(message.message_id_header)
                ):
                    skipped_message_ids.append(reference.message_id)
                    continue

                processed_at = _utc_now()
                sender = message.sender.email if message.sender is not None else ""
                processed_items.append(
                    RunItem(
                        message_id=reference.message_id,
                        thread_id=message.thread_id,
                        received_at=message.sent_at,
                        subject=message.subject,
                        sender=sender,
                        summary=_summarize_body(message.body_text),
                        status="dry-run" if effective_dry_run else "processed",
                        processed_at=processed_at,
                    )
                )

            if processed_items:
                sheet_result = self.client.write_rows(
                    config.sheet_id,
                    config.sheet_range,
                    [item.to_sheet_row() for item in processed_items],
                    dry_run=effective_dry_run,
                )
                if not effective_dry_run:
                    for item in processed_items:
                        self.state_store.mark_processed(
                            item.message_id,
                            run_id=run_id,
                            processed_at=item.processed_at,
                            thread_id=item.thread_id,
                        )

            provisional_summary = RunSummary(
                run_id=run_id,
                started_at=started_at,
                finished_at=started_at,
                dry_run=effective_dry_run,
                query=config.gmail_query,
                matched_count=len(search_result.messages),
                processed_count=len(processed_items),
                skipped_count=len(skipped_message_ids),
                failed_count=len(failures),
                processed_items=tuple(processed_items),
                skipped_message_ids=tuple(skipped_message_ids),
                failures=tuple(failures),
                sheet_write=sheet_result,
                digest_send=None,
            )
            digest = build_digest(
                provisional_summary,
                recipient=config.digest_recipient,
                subject=config.digest_subject,
            )
            digest_result = self.client.send_digest(digest, dry_run=effective_dry_run)
            self.state_store.record_digest(
                run_id,
                recipient=config.digest_recipient,
                status="dry_run_preview" if effective_dry_run else "sent",
                sent_at=_utc_now(),
                message_id=digest_result.message_id,
                draft_id=digest_result.draft_id,
            )

            if failures:
                status = "partial"
                notes = "\n".join(failures)
        except Exception as exc:
            status = "failed"
            failures.append(str(exc))
            notes = str(exc)
            raise
        finally:
            finished_at = _utc_now()
            self.state_store.finish_run(
                run_id,
                finished_at=finished_at,
                matched_count=len(processed_items) + len(skipped_message_ids) + len(failures),
                processed_count=len(processed_items),
                skipped_count=len(skipped_message_ids),
                failed_count=len(failures),
                status=status,
                notes=notes,
            )

        return RunSummary(
            run_id=run_id,
            started_at=started_at,
            finished_at=finished_at,
            dry_run=effective_dry_run,
            query=config.gmail_query,
            matched_count=len(processed_items) + len(skipped_message_ids) + len(failures),
            processed_count=len(processed_items),
            skipped_count=len(skipped_message_ids),
            failed_count=len(failures),
            processed_items=tuple(processed_items),
            skipped_message_ids=tuple(skipped_message_ids),
            failures=tuple(failures),
            sheet_write=sheet_result,
            digest_send=digest_result,
        )
