from __future__ import annotations

from pathlib import Path

from packages.config import load_run_config


def test_load_run_config_reads_yaml_file(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
gmail_query: from:test@example.com
sheet_id: sheet-123
sheet_range: Test!A1
digest_recipient: digest@example.com
max_results: 3
dry_run_default: false
state_db_path: runtime/state/test.sqlite3
digest_subject: Local digest
""".strip()
    )

    config = load_run_config(config_path)

    assert config.gmail_query == "from:test@example.com"
    assert config.sheet_id == "sheet-123"
    assert config.sheet_range == "Test!A1"
    assert config.digest_recipient == "digest@example.com"
    assert config.max_results == 3
    assert config.dry_run_default is False
    assert config.state_db_path == Path("runtime/state/test.sqlite3")
    assert config.digest_subject == "Local digest"


def test_load_run_config_allows_environment_overrides(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
gmail_query: from:file@example.com
sheet_id: sheet-file
sheet_range: File!A1
digest_recipient: file@example.com
""".strip()
    )

    config = load_run_config(
        config_path,
        env={
            "GWS_HARNESS_GMAIL_QUERY": "from:env@example.com",
            "GWS_HARNESS_MAX_RESULTS": "9",
            "GWS_HARNESS_DRY_RUN": "true",
        },
    )

    assert config.gmail_query == "from:env@example.com"
    assert config.max_results == 9
    assert config.dry_run_default is True
