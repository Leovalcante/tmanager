from click.testing import CliRunner
from tmanager.tman import tman

runner = CliRunner()


def test_tman_find_help():
    result = runner.invoke(tman, ["find", "--help"])
    assert result.exit_code == 0
