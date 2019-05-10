from click.testing import CliRunner
from tmanager.tman import tman

runner = CliRunner()


def test_tman_config_help():
    result = runner.invoke(tman, ["config", "--help"])
    assert result.exit_code == 0
