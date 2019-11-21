import importlib

import click

from tmanager import tman_version, tman_name_desc
from tmanager.core.config import Config


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(tman_version, "-V", "--version", prog_name=tman_name_desc)
@click.pass_context
def tman(ctx: click.core.Context) -> None:
    """
    \b
    Tman - Tool Manager:
        Manage all the files and repositories you want, quickly
        and in a handy way.
        Keep your repos up-to-date and bring your tools and configurations
        wherever you wish.
    \b
        One Tool to rule them all, One Tool to find them,
        One Tool to bring them all and in the darkness bind them.
    \f

    :param click.core.Context ctx: click context
    :return: None
    """
    # Check that context object type is dict
    ctx.ensure_object(dict)

    # Add config object and verbose flag to context
    config = Config()
    config.load()
    ctx.obj["config"] = config


# Dynamically add tman commands
commands = [
    "add",
    "install",
    "update",
    "find",
    "config",
    "delete",
    "modify",
    "scan",
    "import_conf",
    "export_conf"
]
for command in commands:
    module = importlib.import_module(f"tmanager.commands.{command}")
    command_function = getattr(module, command)
    tman.add_command(command_function)

# TODO: In order to edit and detached version just for command instead of tman, should we add also command version??????
