import importlib

import click

from tmanager import version, name_desc
from tmanager.core.config import Config


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option("-v", "--verbose", is_flag=True, help="Execute command in verbose mode.")
@click.version_option(version, "-V", "--version", prog_name=name_desc, )
@click.pass_context
def tman(ctx: click.core.Context, verbose: bool) -> None:
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


# Dynamically add tman commands
commands = [
    'add',
    'install',
    'update',
    'find',
    'config',
    'delete',
    'modify',
    'scan',
    'import_conf',
    'export_conf'
]
for command in commands:
    module = importlib.import_module(f'tmanager.commands.{command}')
    command_function = getattr(module, command)
    tman.add_command(command_function)


# MAIN
if __name__ == "__main__":
    tman()
