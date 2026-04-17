from __future__ import annotations

from packages.google_workspace import DigestMessage
from packages.runner.models import RunSummary


def build_digest(summary: RunSummary, *, recipient: str, subject: str) -> DigestMessage:
    mode_label = "dry run" if summary.dry_run else "live run"
    lines = [
        f"Run timestamp: {summary.started_at}",
        f"Query used: {summary.query}",
        "",
        "Counts:",
        f"- matched messages: {summary.matched_count}",
        f"- processed messages: {summary.processed_count}",
        f"- skipped messages: {summary.skipped_count}",
        f"- failed messages: {summary.failed_count}",
        "",
        f"This was a {mode_label}.",
        "",
        "Processed rows:",
    ]

    if summary.processed_items:
        for item in summary.processed_items:
            lines.append(
                f"- {item.subject or '(no subject)'} | {item.sender} | {item.summary}"
            )
    else:
        lines.append("- none")

    return DigestMessage.create(to=[recipient], subject=subject, body="\n".join(lines))
