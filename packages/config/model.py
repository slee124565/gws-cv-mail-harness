from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunConfig:
    gmail_query: str
    sheet_id: str
    sheet_range: str
    digest_recipient: str
    max_results: int = 20
    dry_run_default: bool = True
    state_db_path: Path = Path("runtime/state/gws_cv_mail_harness.sqlite3")
    digest_subject: str = "gws-cv-mail-harness digest"
