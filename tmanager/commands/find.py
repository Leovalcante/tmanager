import datetime
import sys
import time

import click

from tmanager.core.messages import Prints, Echoes
from tmanager.utilities import commands as utl_cmd

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

    vrb = utl_cmd.get_verbose_from_context(ctx)

    # if a filename for logs is provided, then make sure it exists and it's writable.
    log_file_name = ""
    if log:
        log_file_name = utl_cmd.validate_log_filename(log, CMD_NAME)
        if not log_file_name:
            # TODO: Print an error message
            sys.exit(1)

    cfg = utl_cmd.get_configs_from_context(ctx)

    # Convert the date to epoch time if it's not None
    if last_update_date:
        if "/" in last_update_date:
            # Accept the format dd/mm/yyyy, though it gets converted
            last_update_date = last_update_date.replace("/", "-")

        last_update_date = _date_to_epoch(last_update_date)

    if all:
        # Retrieve all the tools
        tools = cfg.get_tools()

    else:
        # Retrieve tools that match searching criteria
        tools = utl_cmd.find_tool(cfg, url=url, tags=tags, name=name, type=type,
                                  last_update_date=last_update_date, f=True)

    # Total. tools found
    tot = 0
    if tools:
        Prints.info("Tools found:", cmd_name=CMD_NAME, log_file_name=log_file_name)
        for tool in tools:
            Prints.info(str(tool) if not vrb else tool.__str__(vrb), show_icon=False,
                        cmd_name=CMD_NAME, log_file_name=log_file_name)
            tot += 1

    if not all:
        # Print summary if all is set
        Prints.info(f"Found {tot}/{len(cfg.get_tools())} tools", show_icon=False,
                    cmd_name=CMD_NAME, log_file_name=log_file_name)

    elif tot != 0:
        Prints.info(f"Tot tools: {len(tools)}", show_icon=False, cmd_name=CMD_NAME, log_file_name=log_file_name)

    else:
        # The case where all is set, and there's no tool registered
        Prints.info("Nothing found", cmd_name=CMD_NAME, log_file_name=log_file_name)
    sys.exit(0)


def _date_to_epoch(date_time: str) -> float:
    """
    Returns the 'epoch-time' equivalent of the date taken as a parameter.

    :param str date_time: date to convert in epoch. It MUST BE in dd-mm-yyyy format
    :return float: seconds to epoch
    """
    try:
        date_time = str(datetime.datetime.strptime(date_time, '%d-%m-%Y')).split(" ")[0]
    except ValueError:
        raise click.BadParameter(Echoes.error("Bad data format! It must be dd-mm-yyyy"), param="--last-update-date",
                                 param_hint="Date format MUST BE dd-mm-yyyy")

    date_time = f"{date_time}-0-0-0-0-0-0"
    # noinspection PyTypeChecker
    date_time = time.mktime(tuple([int(e) for e in date_time.split("-")]))

    return date_time
