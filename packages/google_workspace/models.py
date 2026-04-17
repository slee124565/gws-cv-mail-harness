from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


def _string_tuple(value: Sequence[str] | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(str(item) for item in value)


@dataclass(frozen=True)
class RequestPreview:
    method: str
    url: str
    query_params: tuple[tuple[str, str], ...] = ()
    body: Any | None = None
    dry_run: bool = True
    is_multipart_upload: bool = False

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "RequestPreview":
        query_params = tuple(
            (str(name), str(value))
            for name, value in payload.get("query_params", [])
        )
        return cls(
            method=str(payload.get("method", "")),
            url=str(payload.get("url", "")),
            query_params=query_params,
            body=payload.get("body"),
            dry_run=bool(payload.get("dry_run", False)),
            is_multipart_upload=bool(payload.get("is_multipart_upload", False)),
        )


@dataclass(frozen=True)
class AuthStatus:
    user: str | None
    auth_method: str | None
    credential_source: str | None
    token_valid: bool
    client_config_exists: bool
    encrypted_credentials_exists: bool
    has_refresh_token: bool
    scope_count: int
    scopes: tuple[str, ...] = ()

    @property
    def is_usable(self) -> bool:
        return self.token_valid and self.client_config_exists and self.has_refresh_token

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "AuthStatus":
        return cls(
            user=payload.get("user"),
            auth_method=payload.get("auth_method"),
            credential_source=payload.get("credential_source"),
            token_valid=bool(payload.get("token_valid", False)),
            client_config_exists=bool(payload.get("client_config_exists", False)),
            encrypted_credentials_exists=bool(payload.get("encrypted_credentials_exists", False)),
            has_refresh_token=bool(payload.get("has_refresh_token", False)),
            scope_count=int(payload.get("scope_count", 0)),
            scopes=_string_tuple(payload.get("scopes")),
        )


@dataclass(frozen=True)
class MessageRef:
    message_id: str
    thread_id: str | None = None
    internal_date: str | None = None
    subject: str | None = None
    snippet: str | None = None

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "MessageRef":
        return cls(
            message_id=str(payload.get("id", payload.get("message_id", ""))),
            thread_id=payload.get("threadId", payload.get("thread_id")),
            internal_date=payload.get("internalDate", payload.get("internal_date")),
            subject=payload.get("subject"),
            snippet=payload.get("snippet"),
        )


@dataclass(frozen=True)
class SearchMessagesResult:
    messages: tuple[MessageRef, ...] = ()
    result_size_estimate: int | None = None
    next_page_token: str | None = None
    request_preview: RequestPreview | None = None


@dataclass(frozen=True)
class MessageAddress:
    email: str
    name: str | None = None

    @classmethod
    def from_payload(cls, payload: Any | None) -> "MessageAddress | None":
        if payload is None:
            return None
        if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
            if not payload:
                return None
            return cls.from_payload(payload[0])
        if not isinstance(payload, Mapping):
            return None
        return cls(email=str(payload.get("email", "")), name=payload.get("name"))


@dataclass(frozen=True)
class MessagePacket:
    gmail_message_id: str
    message_id_header: str | None = None
    thread_id: str | None = None
    subject: str | None = None
    sent_at: str | None = None
    sender: MessageAddress | None = None
    reply_to: MessageAddress | None = None
    to: tuple[MessageAddress, ...] = ()
    cc: tuple[MessageAddress, ...] = ()
    references: tuple[str, ...] = ()
    body_text: str | None = None
    body_html: str | None = None

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "MessagePacket":
        to_addresses = tuple(
            address
            for item in payload.get("to", []) or []
            if (address := MessageAddress.from_payload(item)) is not None
        )
        cc_addresses = tuple(
            address
            for item in payload.get("cc", []) or []
            if (address := MessageAddress.from_payload(item)) is not None
        )
        return cls(
            gmail_message_id=str(payload.get("id", "")),
            message_id_header=payload.get("message_id"),
            thread_id=payload.get("thread_id", payload.get("threadId")),
            subject=payload.get("subject"),
            sent_at=payload.get("date"),
            sender=MessageAddress.from_payload(payload.get("from")),
            reply_to=MessageAddress.from_payload(payload.get("reply_to")),
            to=to_addresses,
            cc=cc_addresses,
            references=_string_tuple(payload.get("references")),
            body_text=payload.get("body_text"),
            body_html=payload.get("body_html"),
        )


@dataclass(frozen=True)
class SheetWriteResult:
    spreadsheet_id: str | None = None
    table_range: str | None = None
    updated_range: str | None = None
    updated_rows: int = 0
    updated_columns: int = 0
    updated_cells: int = 0
    request_preview: RequestPreview | None = None

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "SheetWriteResult":
        updates = payload.get("updates", {}) or {}
        return cls(
            spreadsheet_id=payload.get("spreadsheetId"),
            table_range=payload.get("tableRange"),
            updated_range=updates.get("updatedRange"),
            updated_rows=int(updates.get("updatedRows", 0)),
            updated_columns=int(updates.get("updatedColumns", 0)),
            updated_cells=int(updates.get("updatedCells", 0)),
        )


@dataclass(frozen=True)
class DigestMessage:
    to: tuple[str, ...]
    subject: str
    body: str
    cc: tuple[str, ...] = ()
    bcc: tuple[str, ...] = ()
    from_email: str | None = None
    html: bool = False
    attachments: tuple[str, ...] = ()

    @classmethod
    def create(
        cls,
        *,
        to: Sequence[str],
        subject: str,
        body: str,
        cc: Sequence[str] | None = None,
        bcc: Sequence[str] | None = None,
        from_email: str | None = None,
        html: bool = False,
        attachments: Sequence[str] | None = None,
    ) -> "DigestMessage":
        return cls(
            to=_string_tuple(to),
            subject=subject,
            body=body,
            cc=_string_tuple(cc),
            bcc=_string_tuple(bcc),
            from_email=from_email,
            html=html,
            attachments=_string_tuple(attachments),
        )


@dataclass(frozen=True)
class SendResult:
    message_id: str | None = None
    thread_id: str | None = None
    label_ids: tuple[str, ...] = field(default_factory=tuple)
    draft_id: str | None = None
    request_preview: RequestPreview | None = None

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "SendResult":
        return cls(
            message_id=payload.get("id", payload.get("message_id")),
            thread_id=payload.get("threadId", payload.get("thread_id")),
            label_ids=_string_tuple(payload.get("labelIds", payload.get("label_ids"))),
            draft_id=payload.get("draftId", payload.get("draft_id")),
        )
