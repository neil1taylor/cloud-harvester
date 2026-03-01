# tests/test_auth.py
from unittest.mock import patch, MagicMock
from cloud_harvester.auth import authenticate


def test_authenticate_returns_token():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "test-token",
        "token_type": "Bearer",
        "expires_in": 3600,
    }

    with patch("cloud_harvester.auth.requests.post", return_value=mock_response):
        token = authenticate("test-api-key")
        assert token == "test-token"


def test_authenticate_raises_on_invalid_key():
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = Exception("Bad Request")

    with patch("cloud_harvester.auth.requests.post", return_value=mock_response):
        try:
            authenticate("bad-key")
            assert False, "Should have raised"
        except Exception:
            pass
