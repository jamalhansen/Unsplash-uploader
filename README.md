# Unsplash Uploader

Uploads photos to Unsplash via the API, given a config file with credentials.

## Features

- Simple CLI for uploading images: `uv run upload-unsplash --file photo.jpg`.
- Credentials stored in `~/.config/unsplash/config.toml` or environment variables.
- Supports description and comma-separated tags.
- Prints the Unsplash photo URL on success.
- Standard local-first tracking.

## Configuration

Credentials can be set via environment variables:
- `UNSPLASH_ACCESS_KEY`
- `UNSPLASH_SECRET_KEY`
- `UNSPLASH_BEARER_TOKEN` (for OAuth write access)

Or in `~/.config/unsplash/config.toml`:
```toml
access_key = "..."
secret_key = "..."
bearer_token = "..."
```

## Usage

```bash
# Basic upload
uv run upload-unsplash --file photo.jpg --description "Morning fog over the bay"

# Upload with tags
uv run upload-unsplash --file photo.jpg --description "Golden Gate Bridge" --tags "san-francisco,bridge,fog"

# Dry run (validate config and file existence)
uv run upload-unsplash --file photo.jpg --dry-run
```

## Development

```bash
# Run tests (using MagicMock for API)
uv run pytest
```

## Part of the Photo Pipeline
`photo-renamer` → `photo-metadata-scrubber` → `photo-scaler` → `unsplash-uploader`
