from __future__ import annotations

import json
from typing import Any, Sequence

from .command_runner import GWSCommandRunner
from .models import (
    AuthStatus,
    DigestMessage,
    MessagePacket,
    MessageRef,
    RequestPreview,
    SearchMessagesResult,
    SendResult,
    SheetWriteResult,
)


class GoogleWorkspaceClient:
    def __init__(self, runner: GWSCommandRunner | None = None) -> None:
        self.runner = runner or GWSCommandRunner()

    def preflight(self) -> AuthStatus:
        payload = self.runner.run_json(["auth", "status"])
        return AuthStatus.from_payload(payload)

    def search_messages(
        self,
        query: str,
        max_results: int,
        *,
        user_id: str = "me",
        include_spam_trash: bool = False,
        dry_run: bool = False,
    ) -> SearchMessagesResult:
        params: dict[str, Any] = {"userId": user_id, "maxResults": max_results}
        if query:
            params["q"] = query
        if include_spam_trash:
            params["includeSpamTrash"] = True

        args = [
            "gmail",
            "users",
            "messages",
            "list",
            "--params",
            json.dumps(params, separators=(",", ":")),
        ]
        if dry_run:
            args.append("--dry-run")

        payload = self.runner.run_json(args)
        if payload.get("dry_run"):
            return SearchMessagesResult(request_preview=RequestPreview.from_payload(payload))

        messages = tuple(MessageRef.from_payload(item) for item in payload.get("messages", []))
        result_size_estimate = payload.get("resultSizeEstimate")
        return SearchMessagesResult(
            messages=messages,
            result_size_estimate=int(result_size_estimate) if result_size_estimate is not None else None,
            next_page_token=payload.get("nextPageToken"),
        )

    def read_message(
        self,
        message_id: str,
        *,
        include_headers: bool = True,
        html: bool = False,
        dry_run: bool = False,
    ) -> MessagePacket:
        args = ["gmail", "+read", "--id", message_id, "--format", "json"]
        if include_headers:
            args.append("--headers")
        if html:
            args.append("--html")
        if dry_run:
            args.append("--dry-run")

        payload = self.runner.run_json(args)
        if not isinstance(payload, dict):
            raise ValueError("Expected mapping payload from gws gmail +read.")
        payload.setdefault("id", message_id)
        return MessagePacket.from_payload(payload)

    def write_rows(
        self,
        spreadsheet_id: str,
        range_name: str,
        rows: Sequence[Sequence[Any]],
        *,
        dry_run: bool = False,
        value_input_option: str = "USER_ENTERED",
        insert_data_option: str = "INSERT_ROWS",
    ) -> SheetWriteResult:
        params = {
            "spreadsheetId": spreadsheet_id,
            "range": range_name,
            "valueInputOption": value_input_option,
            "insertDataOption": insert_data_option,
        }
        body = {"values": [list(row) for row in rows]}
        args = [
            "sheets",
            "spreadsheets",
            "values",
            "append",
            "--params",
            json.dumps(params, separators=(",", ":")),
            "--json",
            json.dumps(body, separators=(",", ":")),
        ]
        if dry_run:
            args.append("--dry-run")

        payload = self.runner.run_json(args)
        if payload.get("dry_run"):
            return SheetWriteResult(
                spreadsheet_id=spreadsheet_id,
                request_preview=RequestPreview.from_payload(payload),
            )
        return SheetWriteResult.from_payload(payload)

    def send_digest(
        self,
        digest: DigestMessage,
        *,
        dry_run: bool = False,
        draft: bool = False,
    ) -> SendResult:
        args = [
            "gmail",
            "+send",
            "--to",
            ",".join(digest.to),
            "--subject",
            digest.subject,
            "--body",
            digest.body,
        ]
        if digest.cc:
            args.extend(["--cc", ",".join(digest.cc)])
        if digest.bcc:
            args.extend(["--bcc", ",".join(digest.bcc)])
        if digest.from_email:
            args.extend(["--from", digest.from_email])
        if digest.html:
            args.append("--html")
        for attachment in digest.attachments:
            args.extend(["--attach", attachment])
        if dry_run:
            args.append("--dry-run")
        if draft:
            args.append("--draft")

        payload = self.runner.run_json(args)
        if payload.get("dry_run"):
            return SendResult(request_preview=RequestPreview.from_payload(payload))
        return SendResult.from_payload(payload)
