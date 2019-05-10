from click.testing import CliRunner
from tmanager.tman import tman

runner = CliRunner()


def test_tman_update_help():
    result = runner.invoke(tman, ["export-conf", "--help"])
    assert result.exit_code == 0
