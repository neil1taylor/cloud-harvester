# tests/test_harvester.py
from unittest.mock import patch
from cloud_harvester.harvester import run_harvest


def test_run_harvest_authenticates_and_discovers_accounts():
    with patch("cloud_harvester.harvester.authenticate", return_value="token") as mock_auth, \
         patch("cloud_harvester.harvester.get_account_info") as mock_info, \
         patch("cloud_harvester.harvester.collect_account") as mock_collect:

        mock_info.return_value = {"name": "Test", "account_id": "123", "owner_email": "t@t.com"}

        run_harvest(
            api_key="test-key",
            domains=["classic"],
            skip=[],
            accounts=[],
            regions=[],
            output_dir="/tmp",
            concurrency=5,
            resume=False,
            no_cache=True,
        )
        mock_auth.assert_called_once_with("test-key")
        mock_collect.assert_called_once()
