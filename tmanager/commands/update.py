import click
import sys
import tmanager.utilities.commands as utl_cmds
import tmanager.core.messages.messages as msg

CMD_NAME = "update"


@click.command()
@click.option("-n", "--name", help="Update tool by name.", metavar="<tool-name>")
@click.option("-u", "--repo-url", help="Update tool by url.", metavar="<url>")
@click.option("-a", "--all", is_flag=True, help="Update every registered tool.")
@click.option("-l", "--log", help="Log to file instead of printing to stdout.", metavar="<filename>")
@click.option("-y", "--assume-yes", is_flag=True, help="Assume yes.")
@click.pass_context
def update(ctx: click.core.Context, name: str, repo_url: str, all: bool, log: str, assume_yes: bool) -> None:
    """
    Update added tools.
    \f

    :param click.core.Context ctx: click context
    :param str name: name of repository to update
    :param str repo_url: repository url to update
    :param bool all: should update all repositories?
    :param str log: log filename
    :param bool assume_yes: assume positive answer to any user prompt
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

    cfg = utl_cmds.get_configs_from_context(ctx)

    if name:
        # Update by name
        repos = utl_cmds.find_tool(cfg, name=name)

    elif repo_url:
        # Update by URL
        repos = utl_cmds.find_tool(cfg, url=repo_url)

    else:
        # Update everything
        repos = cfg.get_tools(repo_only=True)

    tot_updated = 0
    updated = []
    for repo in repos:
        # skip repo that are not installed
        if not repo.is_installed():
            if not all:
                msg.Prints.warning(f"'{repo.get_name()}' is not installed.", log_fname, CMD_NAME)
            continue
        res = repo.update()
        # already up-to-date
        if res == 1:
            if not all:
                msg.Prints.warning(f"Tool '{repo.get_name()}' is already up to date.", log_fname, CMD_NAME)
        # updated successfully
        elif res == 0:
            tot_updated += 1
            repo_name = repo.get_name()
            updated.append(repo_name)
            if not all:
                msg.Prints.info(f"Tool '{repo_name}' updated successfully.", log_fname, CMD_NAME, icon=False)
        elif res == 5:
            msg.Prints.info(f"No need to update local file '{repo.get_directory()}'", log_fname, CMD_NAME, icon=False)

    if all:
        msg.Prints.info(f"Updated {'' if len(updated) == 0 else f'{str(updated)}, '}{tot_updated}/{len(repos)} repos",
                        log_fname, CMD_NAME, icon=False)

    cfg.save()
    sys.exit(0)
