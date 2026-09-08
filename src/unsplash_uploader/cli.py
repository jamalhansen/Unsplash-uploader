from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from local_first_common.cli import (
    dry_run_option,
    resolve_dry_run,
)
from local_first_common.tracking import register_tool
from .core import (
    upload_to_unsplash,
)

_TOOL = register_tool("unsplash-uploader")

console = Console()
app = typer.Typer(help="Uploads photos to Unsplash via the API.")


@app.command()
def upload(
    file: Annotated[Path, typer.Option("--file", "-f", help="Photo file to upload")],
    description: Annotated[
        str, typer.Option("--description", "-d", help="Photo description")
    ],
    tags: Annotated[
        Optional[str], typer.Option("--tags", "-t", help="Comma-separated tags")
    ] = None,
    dry_run: Annotated[bool, dry_run_option()] = False,
):
    """Upload a photo to Unsplash with metadata."""
    dry_run = resolve_dry_run(dry_run, False)

    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"Preparing upload for {file.name}...",
            title="Unsplash Uploader",
            border_style="cyan",
        )
    )

    if upload_to_unsplash(file, description, tags, dry_run=dry_run):
        if not dry_run:
            console.print("\n[bold green]Upload complete![/bold green]")
    else:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
