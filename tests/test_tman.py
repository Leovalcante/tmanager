from click.testing import CliRunner
from tmanager.tman import tman
from tmanager import __version__
from tests import *

runner = CliRunner()


def test_tman_help():
    result = runner.invoke(tman, ["--help"])
    assert result.exit_code == 0


def test_tman_version():
    result = runner.invoke(tman, ["--version"])
    assert result.exit_code == 0
    assert result.output == "Tool Manager, version {}\n".format(__version__)


def test_tman_version_with_command():
    # Should print tman version though add command selected
    result = runner.invoke(tman, ["--version", "find"])
    assert result.exit_code == 0
    assert result.output == "Tool Manager, version {}\n".format(__version__)


def test_tman_verbose_missing_command():
    result = runner.invoke(tman, ["--verbose"])
    assert result.exit_code != 0
    assert MISSING_COMMAND_ERROR_TEMPLATE in result.output


def test_tman_verbose():
    result = runner.invoke(tman, ["--verbose", "find"])
    assert result.exit_code != 0  # Find error is raised


def test_tman_missing_command():
    # This should print tman help text
    result = runner.invoke(tman)
    assert result.exit_code == 0


def test_tman_wrong_option():
    fake_opt = "--fake-option"
    result = runner.invoke(tman, [fake_opt])
    assert result.exit_code != 0
    assert NO_SUCH_OPTION_ERROR_TEMPLATE.format(fake_opt) in result.output


def test_tman_wrong_command():
    fake_cmd = "fake-command"
    result = runner.invoke(tman, [fake_cmd])
    assert result.exit_code != 0
    assert NO_SUCH_COMMAND_ERROR_TEMPLATE.format(fake_cmd) in result.output
