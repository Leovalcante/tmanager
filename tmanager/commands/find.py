import click
import sys
import tmanager.utilities.commands as utl_cmds
import tmanager.utilities.dates as utl_dates
import tmanager.core.messages.messages as msg

CMD_NAME = "find"


@click.command()
@click.option("-u", "--url", help="Find repository by url.", metavar="<url>")
@click.option("-t", "--tags", help="Find all so-tagged repository.", metavar="<t1,t2,...,tN>")
@click.option("-n", "--name", multiple=True, help="Find tool by name.", metavar="<tool-name>")
@click.option("-p", "--type", multiple=True, help="Find tool by type.", metavar="<type-name>")
@click.option("-d", "--last-update-date",
              help="Find repository having last update date greater then the one insert.", metavar="dd-mm-yyyy")
@click.option("-a", "--all", is_flag=True, help="List all the tools.")
@click.option("-l", "--log", help="Log to file instead of printing to stdout.", metavar="<filename>")
@click.pass_context
def find(ctx: click.core.Context, url: str, tags: str, name: str, type: str, last_update_date: str, all: bool,
         log: str) -> None:
    """
    Find tools.
    \f

    :param click.core.Context ctx: click context
    :param str url: tool url
    :param str tags: tool tags
    :param str name: tool name
    :param str type: tool type
    :param str last_update_date: tool last update date
    :param bool all: should print all tools
    :param str log: log filename
    :return: None
    """
    if not all and (not url and not tags and not name and not type and not last_update_date):
        all = True

    vrb = utl_cmds.get_verbose_from_context(ctx)

    # if a filename for logs is provided, then make sure it exists and it's writable.
    log_fname = ""
    if log:
        log_fname = utl_cmds.validate_log_filename(log, CMD_NAME)
        if not log_fname:
            sys.exit(1)

    cfg = utl_cmds.get_configs_from_context(ctx)

    # Convert the date to epoch time if it's not None
    if last_update_date:
        if "/" in last_update_date:
            # Accept the format dd/mm/yyyy, though it gets converted
            last_update_date = last_update_date.replace("/", "-")

        last_update_date = utl_dates.date_to_epoch(last_update_date)

    if all:
        # Retrieve all the tools
        tools = cfg.get_tools()

    else:
        # Retrieve tools that match searching criteria
        tools = utl_cmds.find_tool(cfg, url=url, tags=tags, name=name, type=type, last_update_date=last_update_date,
                                   f=True)

    # Total. tools found
    tot = 0
    if tools:
        msg.Prints.info("Tools found:", log_fname, CMD_NAME)
        for tool in tools:
            msg.Prints.info(str(tool) if not vrb else tool.__str__(vrb), log_fname, CMD_NAME, icon=False)
            tot += 1
        print("")  # TODO: replace this print

    if not all:
        # Print summary if all is set
        msg.Prints.info(f"Found {tot}/{len(cfg.get_tools())} tools", log_fname, CMD_NAME, icon=False)

    elif tot != 0:
        msg.Prints.info(f"Tot tools: {len(tools)}", log_fname, CMD_NAME, icon=False)

    else:
        # The case where all is set, and there's no tool registered
        msg.Prints.info("Nothing found", log_fname, CMD_NAME)
    sys.exit(0)
