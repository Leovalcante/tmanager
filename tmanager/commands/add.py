import os
import sys
import click
import time
import tmanager.core.messages.messages as msg
import tmanager.utilities.commands as utl_cmds
import tmanager.utilities.file_system as utl_fs

from srblib import abs_path
from tmanager.core.tool.repository.repository import Repository
from tmanager.core.tool.localfile.localfile import LocalFile
from tmanager.core.tool.tool import Tool
from tmanager.core.config.config import Config

CMD_NAME = "add"


@click.command()
@click.argument("tool", required=False, metavar="[repo_url|local_pathname]")
@click.option("-t", "--tags", help="Specify tool tags", metavar="<t1,t2,...,tN>")
@click.option("-d", "--install-dir", type=click.Path(), help="Specify installation directory.", metavar="<dir>")
@click.option("-i", "--in-file", help="Add tools from file.", metavar="<filename>")
@click.option("-l", "--log", help="Log to file instead of printing to stdout.", metavar="<filename>")
@click.option("-y", "--assume-yes", is_flag=True, help="Assume yes.")
@click.pass_context
def add(ctx: click.core.Context, tool: str, tags: str, install_dir: str, in_file: str, log: str,
        assume_yes: bool) -> None:
    """
    Add new tool(s) to tman.
    \f

    :param click.core.Context ctx: click context
    :param str tool: repository url | local file pathname
    :param str tags: tool tags
    :param str install_dir: tool installation directory
    :param str in_file: tools input file
    :param str log: log filename
    :param bool assume_yes: assume_yes flag
    :return: None
    """
    # If neither in_file nor repo_url is provided (or if they're bot provided), then display the usage and quit
    if not (bool(in_file) != bool(tool)):
        utl_cmds.usage_error(CMD_NAME)
        sys.exit(1)

    # if a filename for logs is provided, then make sure it exists and it's writable.
    log_fname = ""
    if log:
        log_fname = utl_cmds.validate_log_filename(log, CMD_NAME, assume_yes)
        if not log_fname:
            sys.exit(1)

    # Load the configuration file
    cfg = utl_cmds.get_configs_from_context(ctx)

    # Add tools from CSV
    imported_tools = 0
    if in_file:
        tools = parse_tools_from_csv(in_file, cfg.get_default_installation_directory(), assume_yes, log_fname)
        for t in tools:
            if add_tool(cfg, t, log_fname) == 0:
                imported_tools += 1
        msg.Prints.info(f"Successfully imported {imported_tools}/{len(tools)} tools", log_fname, CMD_NAME, icon=False)

    # Add one tool
    else:
        url = tool
        default_dir = cfg.get_default_installation_directory()

        # Sanitize the tag string
        tags = utl_cmds.sanitize_tags(tags)

        # Set installation directory
        directory = install_dir or default_dir

        # Add a trailing slash if required
        directory = utl_fs.trailing_slash(abs_path(directory))

        # If the provided directory doesn't exist or it's not writable, then quit
        if not utl_fs.is_writable(directory):
            msg.Prints.warning(f"{directory} doesn't exist or it isn't writable", log_fname, CMD_NAME)
            sys.exit(1)

        # Check whether the tool is a repository or a local file
        if utl_cmds.is_git_url(url):
            # Repository
            tool = Repository(url, directory, tags=tags, add_date=time.time())
        else:
            # Local file
            tool_path = url

            # If the local_file does not exist or it's not writable, then quit
            if not utl_fs.is_writable(tool_path):
                msg.Prints.warning(f"{tool_path} doesn't exist or it's not writable", log_fname, CMD_NAME)
                sys.exit(1)

            # Get the absolute pathname
            tool_path = os.path.abspath(tool_path)

            dst = directory + utl_fs.get_file_name(tool_path) if directory != default_dir else \
                default_dir + utl_fs.get_file_name(tool_path)

            # If the destination directory is provided by user
            if tool_path != directory and install_dir is not None:
                if os.path.exists(dst):
                    # Prompt confirm if it exists already
                    if not assume_yes \
                            and not click.confirm(msg.Echoes.warning(f"{dst} already exists, overwrite it?")):
                        sys.exit(1)

                # If the tools is not managed yet, then move file
                if not cfg.has_tool(utl_fs.get_file_name(tool_path)):
                    if os.path.isdir(tool_path):
                        utl_fs.delete_from_fs(dst)
                        utl_fs.move_file(tool_path, dst)
                    else:
                        # Move the tool
                        utl_fs.move_file(tool_path, dst)

                    # Add trailing slash if requires
                    tool_path = utl_fs.trailing_slash(tool_path)
                    tool_path = directory + tool_path.split("/")[-1]
                    tool = LocalFile(tool_path, tags=tags, add_date=time.time())
                else:
                    msg.Prints.info(f"Tool {utl_fs.get_file_name(tool_path)} is already managed!!!", log_fname,
                                    CMD_NAME)
                    tool = None
            else:
                tool = LocalFile(tool_path, tags=tags, add_date=time.time())

        # Ensure the tool is not None
        if tool is None:
            sys.exit(1)

        # Add the tool to the tman configuration file
        res = add_tool(cfg, tool, log_fname)

        # Display error message
        if res == 0:
            # Everything okay
            msg.Prints.info(f"'{tool.get_name()}' added successfully", log_fname, CMD_NAME)
            sys.exit(0)
        elif res == 1:
            msg.Prints.warning(f"'{tool.get_name()}' not cloned, '{tool.get_directory()}' already exists!", log_fname,
                               CMD_NAME)
        elif res == 2:
            msg.Prints.warning(f"{tool.get_name()} not cloned, {tool.get_url()} seems not valid", log_fname, CMD_NAME)
        elif res == 3:
            # Tool managed 'directly/indirectly'
            msg.Prints.warning(f"'{tool.get_name()}' is already managed by tman", log_fname, CMD_NAME)
        elif res == 5:
            # Local file does not exists
            msg.Prints.warning(f"'{tool.get_name()}' does not exist", log_fname, CMD_NAME)
        elif res == 6:
            msg.Prints.warning(f"'{tool.get_directory()}' contains repositories that are already managed", log_fname,
                               CMD_NAME)
        else:
            # Possible not managed errors
            msg.Prints.info(f"ERRCODE {res}...", log_fname, CMD_NAME, icon=False)
        sys.exit(1)

    sys.exit(0)


def parse_tools_from_csv(repositories_file: str, default_install_dir: str, assume_yes: bool, log_fname: str) -> list:
    """
    Parses the input file and returns a list containing the read tools

    Every line of the CSV input file must be formatted as detailed below:

        repo_url,t1,t2,....,tN,d=/path/to/my/dir

    Note that the last value (d=...) is completely optional

    :param str repositories_file: path to repositories file
    :param str default_install_dir: path to default installation directory
    :param bool assume_yes: should assume all positive answer to any confirmation prompt?
    :param str log_fname: log filename
    :return list: repositories list
    """
    # Raise an exception if the provided file does not exist or it's not readable
    if not os.path.exists(repositories_file) or not os.path.isfile(repositories_file):
        raise click.ClickException(
            msg.Echoes.error(f"File {repositories_file} doesn't exist. Please provide a valid path"))

    tools = []
    # Read the file lines
    with open(repositories_file, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Ignore empty strings
        res = list(filter(None, line.split(",")))
        if len(res) == 0:
            continue

        # Retrieve tool's properties
        url = res[0]

        # Get tags
        tags = []
        for t in res[1:]:
            if not t.startswith("d="):
                tags.append(t)

        tags = utl_cmds.sanitize_tags(tags)

        # Get destination directory
        directory = default_install_dir
        if res[-1].startswith("d="):
            directory = abs_path(res[-1].split("=")[1])
            directory = utl_fs.trailing_slash(directory)

        dst_dir = directory + utl_fs.get_file_name(url)

        # Instantiate a Tool object, depending on it's kind
        tool = None
        if utl_cmds.is_git_url(url):
            tool = Repository(url, directory, tags=tags, add_date=time.time())
        else:
            tool_path = url
            # If tool_path != directory, then move the local tool
            if tool_path != dst_dir:
                if not os.path.exists(tool_path):
                    msg.Prints.info(f"Cannot add {tool_path}, pathname does not exist.", log_fname, CMD_NAME)
                    continue
                if os.path.exists(dst_dir):
                    msg.Prints.info(f"{dst_dir} exists, what to do?", log_fname, CMD_NAME, icon=False)

                    # If assume_yes is set, do not prompt anything and overwrite
                    # If assume_yes is not set, then ask for confirmation
                    if assume_yes or click.confirm(msg.Echoes.input(f"Overwrite '{dst_dir}'?")):
                        msg.Prints.info(f"Moving {tool_path} into {dst_dir}", log_fname, CMD_NAME, icon=False)
                        utl_fs.delete_from_fs(dst_dir)
                        utl_fs.move_file(tool_path, dst_dir)
                        tool = LocalFile(dst_dir, tags=tags, add_date=time.time())
                    else:
                        tool = None

                # Move the file/dir if it doesn't exist!
                else:
                    # Move the tool
                    utl_fs.move_file(tool_path, dst_dir)
                    tool = LocalFile(tool_path, tags=tags, add_date=time.time())

        if tool is not None:
            tools.append(tool)

    return tools


def add_tool(cfg: Config, tool: Tool, log_fname: str) -> int:
    """
    Add a tool in tman configurations, if automatic_install is set
    then the tool is installed too

        It returns 0 on success, otherwise one of the following error
        code is returned.

        1 -- destination dir. already exists      (auto_install only)
        2 -- the URL seems incorrect              (auto_install only)
        3 -- tool/repo already managed
        5 -- local tool does not exists!!
        6 -- not added, contains repository/ies already managed


    :param Tool tool: repository Repository
    :param Config cfg: configuration Config
    :param str log_fname: log filename
    :return int: status code
    """
    tools_to_delete = []

    # If it is a local file
    if tool.is_localfile():
        # Make sure the tool exists
        if not os.path.exists(tool.get_directory()):
            return 5
        # check if it's a directory
        elif os.path.isdir(tool.get_directory()):
            # check if there's any child repository already managed by tman
            for repo in cfg.get_tools(repo_only=True):
                if repo.get_directory().startswith(tool.get_directory()):
                    return 6
            # otherwise remove any local file that is also managed by tman (already)
            for t in cfg.get_tools():
                if t.is_localfile() and t.get_directory().startswith(tool.get_directory()):
                    tools_to_delete.append(t)

    # Check if the tool is already managed
    if cfg.already_managed(tool):
        return 3

    for t in tools_to_delete:
        cfg.remove_tool(t)

    # If automatic_install is set, then try to clone the repository
    if cfg.get_automatic_install() and tool.is_git_repo():
        res = tool.clone()
        # If everything is okay, then add the defined new tool into the .config file
        if res == 0:
            tool.set_install_date(time.time())
            tool.set_last_update_date(time.time())

            # Add the repository only if clone
            cfg.add_tool(tool)
            cfg.save()
            msg.Prints.success(f"Repository '{tool.get_name()}' cloned successfully into {tool.get_directory()}",
                               log_fname, CMD_NAME)

            return 0

        # Display error message and quit for any other outcome
        elif res == 12:
            # Cloning issue: directory already exists
            return 1
        else:
            return 2
    else:
        cfg.add_tool(tool)
        cfg.save()
        return 0
