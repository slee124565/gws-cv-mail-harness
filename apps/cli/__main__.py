import typer


app = typer.Typer(help="CLI for gws-cv-mail-harness.")


@app.command("preflight")
def preflight() -> None:
    """Placeholder preflight command."""
    typer.echo("preflight not implemented yet")


@app.command("run-once")
def run_once(dry_run: bool = False) -> None:
    """Placeholder single-run command."""
    typer.echo(f"run-once not implemented yet; dry_run={dry_run}")


if __name__ == "__main__":
    app()
