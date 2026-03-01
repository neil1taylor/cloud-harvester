from click.testing import CliRunner
from cloud_harvester.cli import main


def test_cli_requires_api_key():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code != 0
    assert "api-key" in result.output.lower() or "IBMCLOUD_API_KEY" in result.output.lower()


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "api-key" in result.output.lower()
