import os
from pathlib import Path
from typing import Optional

import requests
import toml
from rich.console import Console

console = Console()


class UnsplashError(Exception):
    """Base typed error for unsplash-uploader."""


class UploadError(UnsplashError):
    """Raised when a photo upload to Unsplash fails."""


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
        console.print(
            "[red]Error: Unsplash credentials not found. Please set UNSPLASH_ACCESS_KEY or update config.toml[/red]"
        )
        return False

    if dry_run:
        console.print(
            f"[yellow][dry-run] Would upload {file_path.name} to Unsplash.[/yellow]"
        )
        console.print(f"[dim]Description: {description}[/dim]")
        if tags:
            console.print(f"[dim]Tags: {tags}[/dim]")
        return True

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
    except UploadError as e:
        console.print(f"[red]Failed to upload {file_path.name}: {e}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]Failed to upload {file_path.name}: {e}[/red]")
        if hasattr(e, "response") and e.response is not None:
            console.print(f"[dim]{e.response.text}[/dim]")
        return False
