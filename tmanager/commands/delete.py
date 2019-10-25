import sys

import click

from tmanager.core import messages as msg
from tmanager.core.config import Config
from tmanager.core.file_system import FileSystem
from tmanager.utilities import commands as utl_cmd

CMD_NAME = "delete"


@click.command()
@click.option("-n", "--name", help="Delete tool by name.", metavar="<tool-name>")
@click.option("-i", "--input-file", help="Read tool names from input file.", metavar="<pathname>")
@click.option("-a", "--all", is_flag=True, help="Delete all tools.")
@click.option("-l", "--log", help="Log to file instead of printing to stdout.", metavar="<filename>")
@click.option("-y", "--assume-yes", is_flag=True, help="Assume yes.")
@click.pass_context
def delete(ctx: click.core.Context, name: str, input_file: str, all: bool, log: str, assume_yes: bool) -> None:
    """
    Delete tools.
    \f

    :param click.core.Context ctx: click context
    :param str name: tool name to delete
    :param str input_file: file containing tools to delete
    :param bool all: should delete all?
    :param str log: log filename
    :param bool assume_yes: assume yes as the answer for any user prompt
    :return: None
    """
    cfg = utl_cmd.get_configs_from_context(ctx)
    # Make sure that at least one options is set
    if not (bool(name) ^ bool(input_file) ^ bool(all)):
        utl_cmd.usage_error(CMD_NAME)
        sys.exit(1)

    # if a filename for logs is provided, then make sure it exists and it's writable.
    log_file_name = ""
    if log:
        log_file_name = utl_cmd.validate_log_filename(log, CMD_NAME, assume_yes)
        if not log_file_name:
            # TODO: print an error message
            sys.exit(1)

    tools_to_delete = []

    # Retrieve all the managed tools
    tools = cfg.get_tools()

    # Retrieve every tool that has to be removed
    if name:
        # Search by name
        tools_to_delete += utl_cmd.find_tool(cfg, name=name)

    elif input_file:
        # Read tool names from file (one per line)
        try:
            with open(input_file, "r") as f:
                for tool_name in f.readlines():
                    tool_name = tool_name.strip()

                    # Retrieve repos by tool_name
                    tools_to_delete += utl_cmd.find_tool(cfg, name=tool_name)

        except FileNotFoundError:
            raise click.BadOptionUsage("--input-file",
                                       f"The file {input_file} doesn't exist or it isn't readable, try with another one"
                                       )

    # Display an info message if there's no repository to delete
    if (bool(all) is False and len(tools_to_delete) == 0) or (bool(all) and len(tools) == 0):
        msg.Prints.warning("No tool to delete", cmd_name=CMD_NAME, log_file_name=log_file_name)
        sys.exit(1)

    elif bool(all):
        # Delete every tool
        _delete_all(cfg, tools, assume_yes, log_file_name)

    else:
        # Delete the retrieved tools
        for tool in tools_to_delete:
            cfg.remove_tool(tool)
            msg.Prints.success(f"{tool.get_name()} has been removed", cmd_name=CMD_NAME, log_file_name=log_file_name)

            # Ensure the user wishes to delete the tools from file system too
            if tool.is_installed() and (assume_yes or click.confirm(msg.Echoes.input(
                    f"Delete {tool.get_name()} from file system too?"), default=False)):
                FileSystem.delete(tool.get_directory())
                msg.Prints.success(f"{tool.get_name()} successfully deleted from file system!",
                                   cmd_name=CMD_NAME, log_file_name=log_file_name)

    cfg.save()
    sys.exit(0)


def _delete_all(cfg: Config, deleted_tools: list, assume_yes: bool, log_file_name: str) -> None:
    """
    Delete Every managed tool.

    :param Config cfg: tman configuration object
    :param list deleted_tools: tool list to delete
    :param bool assume_yes: assume all positive response for any prompt
    :param str log_file_name: log filename
    :return: None
    """
    # Prompt for confirmation
    delete_all_repos = assume_yes or click.confirm(msg.Echoes.input("Remove every tool from tman?"), default=True)
    if not delete_all_repos:
        raise click.Abort()

    # Remove all the tools
    msg.Prints.info(f"{cfg.remove_all_tools()} tools removed", cmd_name=CMD_NAME, log_file_name=log_file_name)

    # Update the configuration file
    cfg.save()

    # Ensure the user wishes to delete the tools from file system (FS)
    delete_all_file_system = click.confirm(msg.Echoes.input("Delete every tool from the file system?"),
                                           default=False) if not assume_yes else False

    # Delete every tool from the file system if the user confirmed
    if delete_all_file_system:
        for tool in deleted_tools:
            if tool.is_installed():
                FileSystem.delete(tool.get_directory())
                msg.Prints.info(f"{tool.get_directory()} deleted", show_icon=False,
                                cmd_name=CMD_NAME, log_file_name=log_file_name)

    # Let the user decide which tool he wishes to delete permanently!
    elif deleted_tools and not assume_yes:
        msg.Prints.info("Enter comma-separated list of indexes to remove (i.e. 1,3,4)",
                        cmd_name=CMD_NAME, log_file_name=log_file_name)

        for tool in deleted_tools:
            msg.Prints.info(f"[{str(deleted_tools.index(tool) + 1)}]: {tool.get_name()}", show_icon=False,
                            cmd_name=CMD_NAME, log_file_name=log_file_name)

        to_delete = None
        tool_to_save_indexes = click.prompt(">>> ", 'no')
        if tool_to_save_indexes and tool_to_save_indexes.lower() not in ["no", "n", "quit", "q", "none"]:
            # Check if they're all valid numbers
            to_delete = utl_cmd.sanitize_indexes(deleted_tools, tool_to_save_indexes)

            # Delete valid number repos
            for index in to_delete:
                repo = deleted_tools[index]
                FileSystem.delete(repo.get_directory())
                msg.Prints.success(f"{repo.get_name()} deleted successfully from file system",
                                   cmd_name=CMD_NAME, log_file_name=log_file_name)

        if not to_delete:
            msg.Prints.info("No tool will be erased from file system", cmd_name=CMD_NAME, log_file_name=log_file_name)
            sys.exit(1)
    sys.exit(0)
