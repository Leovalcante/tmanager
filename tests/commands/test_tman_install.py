from click.testing import CliRunner
from tmanager.tman import tman

runner = CliRunner()


def test_tman_install_help():
    result = runner.invoke(tman, ["install", "--help"])
    assert result.exit_code == 0
