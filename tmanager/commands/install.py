import click
import sys
import tmanager.utilities.dates as utl_dates
import tmanager.utilities.file_system as utl_fs
import tmanager.utilities.commands as utl_cmds
import tmanager.core.messages.messages as msg

CMD_NAME = "install"


@click.command()
@click.option("-n", "--name", help="Tool name to install.", metavar="<tool-name>")
@click.option("-u", "--repo-url", help="Repo URL to install.", metavar="<url>")
@click.option("-a", "--all", is_flag=True, help="Install all registered tool.")
@click.option("-l", "--log", help="Log to file instead of printing to stdout.", metavar="<filename>")
@click.option("-y", "--assume-yes", is_flag=True, help="Assume yes.")
@click.pass_context
def install(ctx: click.core.Context, name: str, repo_url: str, all: bool, log: str, assume_yes: bool) -> None:
    """
    Install added tools.
    \f

    :param click.core.Context ctx: click context
    :param str name: tool name
    :param str repo_url: tool repository url
    :param bool all: install every tool
    :param str log: log filename
    :param bool assume_yes: assume yes as the answer for any user prompt
    :return: None
    """
    if not name and not repo_url and not all:
        utl_cmds.usage_error(CMD_NAME)
        sys.exit(1)

    # if a filename for logs is provided, then make sure it exists and it's writable.
    log_fname = ""
    if log:
        log_fname = utl_cmds.validate_log_filename(log, CMD_NAME, assume_yes)
        if not log_fname:
            sys.exit(1)

    install_repository(ctx, name, repo_url, all, assume_yes, log_fname)
    sys.exit(0)


def install_repository(ctx: click.core.Context, name: str, repo_url: str, _all: bool, assume_yes: bool,
                       log_fname: str) -> int:
    """
    Install a tool by name, url, or install every managed tool
    This method returns 0 when it terminates successfully, otherwise
    it returns one of the error code shown below.

    1 -- no criteria match

    :param click.core.Context ctx: click context
    :param str name: tool name
    :param str repo_url: tool repository url
    :param bool _all: should install every tool?
    :param bool assume_yes: should assume positive answer to any confirmation prompt?
    :param str log_fname: log filename
    :return int: status code
    """
    cfg = utl_cmds.get_configs_from_context(ctx)

    if name:
        # Find tools by name
        tools = utl_cmds.find_tool(cfg, name=name)

    elif repo_url:
        # Find tools by URL
        tools = utl_cmds.find_tool(cfg, url=repo_url)

    elif _all:
        # Retrieve all the tools
        tools = cfg.get_tools(repo_only=True)

    else:
        tools = []

    # If there's no tool to install, display error message and return
    if len(tools) == 0:
        msg.Prints.warning("There's no tool to install", log_fname, CMD_NAME)
        return 1

    # Install any tool that matches the criteria
    tot_installed = 0
    installed = list()
    for tool in tools:
        if not tool.is_git_repo():
            continue
        # Clone the repository
        res = tool.clone()
        # If everything went fine
        if res == 0:
            tot_installed += 1

            if not _all:
                msg.Prints.info(f"'{tool.get_name()}' cloned successfully", log_fname, CMD_NAME)

            # append the tool name to the installed toolnames list
            installed.append(tool.get_name())
            # Update repo install date and last-update-date
            tool.update_timestamps()
            # Update the configuration file
            cfg.update_tool(tool)

        elif res == 2:
            # If directory found when cloning you've 3 choices:
            #   (1) leave as it is;
            #   (2) delete and clone the repo again;
            #   (3) update the content if and only if it can be updated.
            # Ask the user what to do with the directory found
            # If assume_yes is set, then the default action that is take is (3):update
            choice = click.prompt(msg.Echoes.input(
                f"Directory '{tool.get_directory()}' found, what to do? \n[1] nothing; [2] delete & clone; "
                f"[3] update\n>>>"), default=None) if not assume_yes else "3"

            # NOTE: please wait before modifying this block of code!!!
            if choice == "2":
                # Delete and clone the repo
                msg.Prints.info(f"removing '{tool.get_name()}'..", log_fname, CMD_NAME)
                utl_fs.delete_from_fs(tool.get_directory())
                msg.Prints.info(f"cloning '{tool.get_name()}'..", log_fname, CMD_NAME)
                tool.clone()
                # Update repo install date and last-update-date
                tool.update_timestamps()
                # Update the tool in the conf.
                cfg.update_tool(tool)

            elif choice == "3":
                # Just update the repo content
                msg.Prints.info(f"updating '{tool.get_name()}'.. this may take a while.", log_fname, CMD_NAME,
                                icon=False)
                res = tool.update()

                if tool.get_install_date() is None:
                    tool.set_install_date(utl_dates.now())

                tool.set_last_update_date(utl_dates.now())
                cfg.update_tool(tool)
                if res == 0:
                    msg.Prints.info(f"'{tool.get_name()}' updates successfully", log_fname, CMD_NAME)
                elif res == 1:
                    msg.Prints.info(f"'{tool.get_name()}' is already up-to-date", log_fname, CMD_NAME)
                else:
                    msg.Prints.info(f"An unexpected error has occurred when trying to update {tool.get_name()}",
                                    log_fname, CMD_NAME)
            else:
                # Choice (1): just continue
                continue

    if _all:
        msg.Prints.info(
            f"Installed {'' if tot_installed == 0 else f'{str(installed)}, '}{tot_installed}/{len(tools)} tools",
            log_fname, CMD_NAME, icon=False)

    cfg.save()
    return 0
