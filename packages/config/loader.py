from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

import yaml

from .model import RunConfig


def _parse_bool(value: Any, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _pick(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return None


def load_run_config(
    path: str | Path | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> RunConfig:
    env_map = env or os.environ
    file_data: dict[str, Any] = {}

    if path is not None:
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        loaded = yaml.safe_load(config_path.read_text()) or {}
        if not isinstance(loaded, dict):
            raise ValueError("Config file must contain a mapping at the top level.")
        file_data = dict(loaded)

    gmail_query = _pick(env_map, "GWS_HARNESS_GMAIL_QUERY", "DEFAULT_GMAIL_QUERY") or _pick(
        file_data, "gmail_query"
    )
    sheet_id = _pick(env_map, "GWS_HARNESS_SHEET_ID", "DEFAULT_SHEET_ID") or _pick(
        file_data, "sheet_id"
    )
    sheet_range = _pick(
        env_map, "GWS_HARNESS_SHEET_RANGE", "DEFAULT_SHEET_RANGE"
    ) or _pick(file_data, "sheet_range")
    digest_recipient = _pick(
        env_map, "GWS_HARNESS_DIGEST_RECIPIENT", "DIGEST_RECIPIENT"
    ) or _pick(file_data, "digest_recipient")

    missing = [
        name
        for name, value in (
            ("gmail_query", gmail_query),
            ("sheet_id", sheet_id),
            ("sheet_range", sheet_range),
            ("digest_recipient", digest_recipient),
        )
        if not value
    ]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required config fields: {missing_text}")

    max_results = _pick(env_map, "GWS_HARNESS_MAX_RESULTS", "MAX_RESULTS") or _pick(
        file_data, "max_results"
    )
    dry_run_default = _parse_bool(
        _pick(env_map, "GWS_HARNESS_DRY_RUN", "DRY_RUN_DEFAULT")
        or _pick(file_data, "dry_run_default"),
        default=True,
    )
    state_db_path = _pick(env_map, "GWS_HARNESS_STATE_DB_PATH", "STATE_DB_PATH") or _pick(
        file_data, "state_db_path"
    )
    digest_subject = _pick(env_map, "GWS_HARNESS_DIGEST_SUBJECT") or _pick(
        file_data, "digest_subject"
    )

    return RunConfig(
        gmail_query=str(gmail_query),
        sheet_id=str(sheet_id),
        sheet_range=str(sheet_range),
        digest_recipient=str(digest_recipient),
        max_results=int(max_results) if max_results is not None else 20,
        dry_run_default=dry_run_default,
        state_db_path=Path(str(state_db_path))
        if state_db_path is not None
        else Path("runtime/state/gws_cv_mail_harness.sqlite3"),
        digest_subject=str(digest_subject) if digest_subject is not None else "gws-cv-mail-harness digest",
    )
