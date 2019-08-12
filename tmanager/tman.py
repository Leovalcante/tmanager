#!/usr/bin/env python3
import click
from tmanager import __version__, __name_desc__
from tmanager.core.config.config import Config
from tmanager.commands.add import add
from tmanager.commands.install import install
from tmanager.commands.update import update
from tmanager.commands.find import find
from tmanager.commands.config import config
from tmanager.commands.delete import delete
from tmanager.commands.modify import modify
from tmanager.commands.scan import scan
from tmanager.commands.export_conf import export_conf
from tmanager.commands.import_conf import import_conf


# CLICK COMMANDS
@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option("-v", "--verbose", is_flag=True, help="Execute command in verbose mode.")
@click.version_option(__version__, "-V", "--version", prog_name=__name_desc__,)
@click.pass_context
def tman(ctx: click.core.Context, verbose: bool) -> None:
    """
    \b
    Tman - Tool Manager:
        Manage all the files and repositories you want, quickly
        and in a handy way.
        Keep your repos up-to-date and bring your tools and configurations
        wherever you wish.
    \f

    :param click.core.Context ctx: click context
    :param bool verbose: show verbose messages
    :return: None
    """

    # Check that context object type is dict
    ctx.ensure_object(dict)

    # Add config object and verbose flag to context
    cfg = Config()
    cfg.load()
    ctx.obj["configurations"] = cfg
    ctx.obj["verbose"] = verbose


# Add tman commands
tman.add_command(add)
tman.add_command(install)
tman.add_command(update)
tman.add_command(find)
tman.add_command(config)
tman.add_command(delete)
tman.add_command(modify)
tman.add_command(scan)
tman.add_command(import_conf)
tman.add_command(export_conf)


# MAIN
if __name__ == "__main__":
    tman()
