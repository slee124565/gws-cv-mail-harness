from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import typer

from packages.config import load_run_config
from packages.google_workspace import GoogleWorkspaceClient
from packages.runner import ProcessingRunner
from packages.state_store import SQLiteStateStore


app = typer.Typer(help="CLI for gws-cv-mail-harness.")


def _echo_json(payload: object) -> None:
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))


@app.command("preflight")
def preflight() -> None:
    """Report whether the local Google Workspace environment is usable."""
    client = GoogleWorkspaceClient()
    status = client.preflight()
    _echo_json(asdict(status))
    if not status.is_usable:
        raise typer.Exit(code=1)


@app.command("run-once")
def run_once(
    config: Path = typer.Option(..., exists=True, dir_okay=False, readable=True),
    dry_run: bool | None = typer.Option(None, "--dry-run/--live"),
) -> None:
    """Process one batch using the local config file."""
    run_config = load_run_config(config)
    effective_dry_run = run_config.dry_run_default if dry_run is None else dry_run
    mode_source = "config default" if dry_run is None else "CLI flag"
    mode_label = "dry-run" if effective_dry_run else "live"
    typer.echo(f"[run-once] execution mode: {mode_label} ({mode_source})", err=True)
    if effective_dry_run:
        typer.echo(
            "[run-once] no Google Sheets append or Gmail send will occur; pass --live to perform live writes.",
            err=True,
        )
    client = GoogleWorkspaceClient()
    state_store = SQLiteStateStore(run_config.state_db_path)
    summary = ProcessingRunner(client, state_store).run_once(
        run_config,
        dry_run=effective_dry_run,
    )
    _echo_json(asdict(summary))


@app.command("show-state")
def show_state(
    config: Path = typer.Option(..., exists=True, dir_okay=False, readable=True),
    limit: int = typer.Option(10, min=1, max=100),
) -> None:
    """Show recent run metadata and processed message ids from SQLite state."""
    run_config = load_run_config(config)
    state_store = SQLiteStateStore(run_config.state_db_path)
    payload = {
        "database": str(run_config.state_db_path),
        "runs": [asdict(item) for item in state_store.list_runs(limit=limit)],
        "processed_messages": [
            asdict(item) for item in state_store.list_processed_messages(limit=limit)
        ],
    }
    _echo_json(payload)


if __name__ == "__main__":
    app()
