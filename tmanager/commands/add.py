import os
import sys
import time
from typing import List

import click

from tmanager.commands import add_name, add_name_desc, add_version
from tmanager.core.command import AbstractCommand
from tmanager.core.file_system import FileSystem
from tmanager.core.messages import Prints, Echoes
from tmanager.core.tool import Tool
from tmanager.core.tool.localfile import LocalFile
from tmanager.core.tool.repository import Repository
from tmanager.utilities import commands as utl_cmd


class AddCommand(AbstractCommand):
    def __init__(self):
        super(AddCommand, self).__init__(add_name, add_name_desc, add_version)

    def _add_tool(self, tool: Tool, log_file: str) -> int:
        return 0

    def exec(self, *args):
        # Unpack args
        self.config, tool, tags, install_dir, input_file, log_file_name, assume_yes, verbose = args
        log_file = self.validate_log_file(log_file_name, assume_yes)

        # Add tools from CSV
        if input_file:
            imported_tools = 0
            tools = []  # shit
            for tool in tools:
                if self._add_tool(tool, log_file) == 0:
                    imported_tools += 1

            Prints.info(f"Successfully imported {imported_tools}/{len(tools)} tools", show_icon=False,
                        cmd_name=self.name, log_file=log_file)
        # Add one tool
        else:
            url = tool
            default_dir = self.config.get_default_installation_directory()

            # Sanitize the tag string
            tags = self.sanitize_tags(tags)

            # Get installation directory
            installation_directory = install_dir or default_dir

            # Add a trailing slash
            installation_directory = FileSystem.get_abs_path(installation_directory, trailing_slash=True)

            # If the provided directory doesn't exist or it's not writable, then quit
            if not FileSystem.is_path_writable(installation_directory):
                Prints.error(f"{installation_directory} doesn't exist or it isn't writable",
                             cmd_name=self.name, log_file=log_file)
                sys.exit(1)

            # Check whether the tool is a repository or a local file
            if utl_cmd.is_git_url(url):
                tool = Repository(url, installation_directory, tags=tags, add_date=time.time())
            else:
                tool_path = url

                # If the local_file does not exist or it's not writable, then quit
                if not FileSystem.is_path_writable(tool_path):
                    Prints.error(f"{tool_path} doesn't exist or it's not writable",
                                 cmd_name=self.name, log_file=log_file)
                    sys.exit(1)

                # Get the absolute path
                tool_path = FileSystem.get_abs_path(tool_path)
                tool_basename = FileSystem.get_basename(tool_path)

                destination_dir = installation_directory + tool_basename

                # If the destination directory is provided by user
                if tool_path != installation_directory and install_dir is not None:
                    # Check if directory already exists
                    if os.path.exists(destination_dir):
                        should_overwrite = assume_yes or click.confirm(
                            f"{destination_dir} already exists, do you want to overwrite it", prompt_suffix="?")

                        if not should_overwrite:
                            sys.exit(1)

                    # If the tools is not managed yet, then move file
                    if not self.config.has_tool(tool_basename):
                        if os.path.isdir(tool_path):
                            FileSystem.delete(destination_dir)  # TODO: without user consent?

                        FileSystem.move(tool_path, destination_dir)

                        tool = LocalFile(destination_dir, tags=tags, add_date=time.time())
                    else:
                        Prints.info(f"Tool {FileSystem.get_basename(tool_path)} is already managed!",
                                    cmd_name=self.name, log_file=log_file)
                        tool = None
                else:
                    tool = LocalFile(tool_path, tags=tags, add_date=time.time())

            # Ensure the tool is not None
            if tool is None:
                sys.exit(1)

            # Add the tool to the tman configuration file
            res = self._add_tool(tool, log_file)

            # Display error message
            if res == 0:
                # Everything okay
                Prints.info(f"'{tool.get_name()}' added successfully", cmd_name=self.name, log_file=log_file)
                sys.exit(0)
            elif res == 1:
                Prints.warning(f"'{tool.get_name()}' not cloned, '{tool.get_directory()}' already exists!",
                               cmd_name=self.name, log_file=log_file)
            elif res == 2:
                Prints.warning(f"{tool.get_name()} not cloned, {tool.get_url()} seems not valid",
                               cmd_name=self.name, log_file=log_file)
            elif res == 3:
                # Tool managed 'directly/indirectly'
                Prints.warning(f"'{tool.get_name()}' is already managed by tman", cmd_name=self.name, log_file=log_file)
            elif res == 5:
                # Local file does not exists
                Prints.warning(f"'{tool.get_name()}' does not exist", cmd_name=self.name, log_file=log_file)
            elif res == 6:
                Prints.warning(f"'{tool.get_directory()}' contains repositories that are already managed",
                               cmd_name=self.name, log_file=log_file)
            else:
                # Possible not managed errors
                Prints.info(f"ERRCODE {res}", show_icon=False, cmd_name=self.name, log_file=log_file)
            sys.exit(1)

        sys.exit(0)


@click.command()
@click.argument("tool", required=False, metavar="[repo_url|local_pathname]")
@click.option("-t", "--tags", help="Specify tool tags", metavar="<t1,t2,...,tN>")
@click.option("-d", "--install-dir", type=click.Path(), help="Specify installation directory.", metavar="<dir>")
@click.option("-i", "--input-file", help="Add tools from file.", metavar="<filename>")
@click.option("-l", "--log", "log_file_name", type=click.File("w"), default=AddCommand().get_default_log_file_path(),
              help="Log to file instead of printing to stdout.", metavar="<filename>")
@click.option("-y", "--assume-yes", is_flag=True, help="Assume yes.")
@click.option("-v", "--verbose", is_flag=True, help="Print verbose messages.")
@click.version_option(AddCommand().version, "-V", "--version", prog_name=AddCommand().name_desc)
@click.pass_context
def add(ctx: click.core.Context,
        tool: str,
        tags: str,
        install_dir: str,
        input_file: str,
        log_file_name: str,
        assume_yes: bool,
        verbose: bool) -> None:
    """
    Add new tool(s) to tman.
    \f

    :param click.core.Context ctx: click context
    :param str tool: repository url | local file pathname
    :param str tags: tool tags
    :param str install_dir: tool installation directory
    :param str input_file: tools input file
    :param str log_file_name: log file name
    :param bool assume_yes: assume_yes flag
    :param bool verbose: print verbose messages
    :return: None
    """
    config = AbstractCommand.get_config_from_context(ctx)
    AddCommand().exec(config, tool, tags, install_dir, input_file, log_file_name, assume_yes, verbose)
