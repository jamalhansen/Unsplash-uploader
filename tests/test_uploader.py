from pathlib import Path
from unittest.mock import MagicMock, patch

from unsplash_uploader.logic import upload_to_unsplash

def create_test_file(tmp_path: Path):
    file_path = tmp_path / "photo.jpg"
    file_path.write_text("dummy content")
    return file_path

@patch("unsplash_uploader.logic.load_config")
@patch("unsplash_uploader.logic.requests.post")
def test_upload_to_unsplash_success(mock_post, mock_load_config, tmp_path):
    file_path = create_test_file(tmp_path)
    
    # Mock config
    mock_load_config.return_value = {"access_key": "fake_key"}
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "links": {"html": "https://unsplash.com/photos/123"}
    }
    mock_post.return_value = mock_response
    
    result = upload_to_unsplash(file_path, "A nice photo", "nature,sun")
    
    assert result is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == "Client-ID fake_key"
    assert kwargs["data"]["description"] == "A nice photo"
    assert kwargs["data"]["tags"] == "nature,sun"

@patch("unsplash_uploader.logic.load_config")
def test_upload_to_unsplash_dry_run(mock_load_config, tmp_path):
    file_path = create_test_file(tmp_path)
    mock_load_config.return_value = {"access_key": "fake_key"}
    
    result = upload_to_unsplash(file_path, "Dry run", dry_run=True)
    assert result is True

@patch("unsplash_uploader.logic.load_config")
def test_upload_to_unsplash_no_auth(mock_load_config, tmp_path):
    file_path = create_test_file(tmp_path)
    mock_load_config.return_value = {}
    
    result = upload_to_unsplash(file_path, "No auth")
    assert result is False
