import os
from pathlib import Path
from typing import Annotated, Optional

import requests
import toml
import typer
from rich.console import Console
from rich.panel import Panel

from local_first_common.cli import (
    dry_run_option,
    resolve_dry_run,
)
from local_first_common.tracking import register_tool

_TOOL = register_tool("unsplash-uploader")
console = Console()
app = typer.Typer(help="Uploads photos to Unsplash via the API.")

CONFIG_PATH = Path.home() / ".config" / "unsplash" / "config.toml"

def load_config() -> dict:
    """Load Unsplash configuration from file or environment."""
    config = {}
    if CONFIG_PATH.exists():
        config = toml.load(CONFIG_PATH)
    
    # Environment variable overrides
    if "UNSPLASH_ACCESS_KEY" in os.environ:
        config["access_key"] = os.environ["UNSPLASH_ACCESS_KEY"]
    if "UNSPLASH_SECRET_KEY" in os.environ:
        config["secret_key"] = os.environ["UNSPLASH_SECRET_KEY"]
    if "UNSPLASH_BEARER_TOKEN" in os.environ:
        config["bearer_token"] = os.environ["UNSPLASH_BEARER_TOKEN"]
        
    return config

def save_config(config: dict):
    """Save configuration to ~/.config/unsplash/config.toml."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        toml.dump(config, f)

def get_auth_headers(config: dict) -> dict:
    """Get headers for Unsplash API requests."""
    if "bearer_token" in config:
        return {"Authorization": f"Bearer {config['bearer_token']}"}
    elif "access_key" in config:
        return {"Authorization": f"Client-ID {config['access_key']}"}
    return {}

def upload_to_unsplash(
    file_path: Path,
    description: str,
    tags: Optional[str] = None,
    dry_run: bool = False,
) -> bool:
    """Upload a single photo to Unsplash."""
    config = load_config()
    headers = get_auth_headers(config)

    if not headers:
        console.print("[red]Error: Unsplash credentials not found. Please set UNSPLASH_ACCESS_KEY or update config.toml[/red]")
        return False

    if dry_run:
        console.print(f"[yellow][dry-run] Would upload {file_path.name} to Unsplash.[/yellow]")
        console.print(f"[dim]Description: {description}[/dim]")
        if tags:
            console.print(f"[dim]Tags: {tags}[/dim]")
        return True

    # Unsplash upload flow:
    # 1. POST /photos
    # Note: Real upload requires OAuth 'write_photos' scope.
    # This implementation assumes the bearer token is already obtained or access key is sufficient for dev.
    
    url = "https://api.unsplash.com/photos"
    data = {
        "description": description,
    }
    if tags:
        data["tags"] = tags

    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        result = response.json()

        photo_url = result.get("links", {}).get("html")
        console.print(f"[green]Successfully uploaded {file_path.name}![/green]")
        console.print(f"URL: {photo_url}")
        return True
    except Exception as e:
        console.print(f"[red]Failed to upload {file_path.name}: {e}[/red]")
        if hasattr(e, "response") and e.response is not None:
            console.print(f"[dim]{e.response.text}[/dim]")
        return False

@app.command()
def upload(
    file: Annotated[Path, typer.Option("--file", "-f", help="Photo file to upload")],
    description: Annotated[str, typer.Option("--description", "-d", help="Photo description")],
    tags: Annotated[Optional[str], typer.Option("--tags", "-t", help="Comma-separated tags")] = None,
    dry_run: Annotated[bool, dry_run_option()] = False,
):
    """Upload a photo to Unsplash with metadata."""
    dry_run = resolve_dry_run(dry_run, False)

    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)

    console.print(Panel(f"Preparing upload for {file.name}...", title="Unsplash Uploader", border_style="cyan"))

    if upload_to_unsplash(file, description, tags, dry_run=dry_run):
        if not dry_run:
            console.print("\n[bold green]Upload complete![/bold green]")
    else:
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
