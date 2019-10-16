import sys

import click

from tmanager.core import messages as msg
from tmanager.core.config import Config
from tmanager.core.tool import Tool
from tmanager.utilities import commands as utl_cmd, file_system as utl_fs

CMD_NAME = "modify"


@click.command()
@click.argument("name", metavar="<tool-name>")
@click.option("-d", "--new-dir", help="New destination dir.", metavar="<pathname>")
@click.option("-tA", "--tag-add", help="Add a comma-separated list of tags.", metavar="<t1,t2,..,tN>")
@click.option("-tR", "--tag-rm", help="Remove a comma-separated list of tags.", metavar="<t1,t2,...,tN>")
@click.option("-tM", "--tag-mv", nargs=2, help="Modify an existing tag.", metavar="<old> <new>")
@click.option("-l", "--log", help="Log to file instead of printing to stdout.", metavar="<filename>")
@click.pass_context
def modify(ctx: click.core.Context, name: str, new_dir: str, tag_add: str, tag_rm: str, tag_mv: tuple,
           log: str) -> None:
    """
    Modify installation directory, add, modify and remove tags.
    \f

    :param click.core.Context ctx: click Context
    :param str name: tool name to modify
    :param str new_dir: new directory for the tool
    :param str tag_add: comma separated list of tags to add to tool
    :param str tag_rm: comma separated list of tags to remove from tool
    :param tuple tag_mv: tuple composed by old_tag_name new_tag_name
    :param str log: log filename
    :return: None
    """
    # Make sure that at least one option have been specified
    if not (bool(new_dir) or bool(tag_add) or bool(tag_rm) or bool(tag_mv)):
        utl_cmd.usage_error(CMD_NAME)
        sys.exit(1)

    # if a filename for logs is provided, then make sure it exists and it's writable.
    log_file_name = ""
    if log:
        log_file_name = utl_cmd.validate_log_filename(log, CMD_NAME)
        if not log_file_name:
            sys.exit(1)

    # Load the config. file and set verbose
    cfg = utl_cmd.get_configs_from_context(ctx)
    vrb = utl_cmd.get_verbose_from_context(ctx)

    msg.Prints.verbose(f"Retrieving tool {name}", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)

    # Retrieve tool object
    tool = cfg.get_tool(name)
    if tool is None:
        raise click.ClickException(msg.Echoes.error("There's no such tool. Make sure you wrote the correct name."))

    msg.Prints.verbose(f"Tool {tool.get_name()} found: {str(tool)}", vrb,
                       cmd_name=CMD_NAME, log_file_name=log_file_name)
    msg.Prints.verbose(f"Retrieving {tool.get_name()}'s tags", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)

    # Retrieving tool tags
    tool_tags = tool.get_tags()

    msg.Prints.verbose(f"Tags retrieved: {tool.get_tags()}", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)

    # Attempt to modify installation-directory
    if new_dir:
        msg.Prints.verbose("Changing tool installation directory", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)

        # Make sure the directory exists and is writable.
        if utl_fs.is_writable(new_dir):
            src_dir = tool.get_directory()
            dst_dir = f"{new_dir}{'' if new_dir.endswith('/') else '/'}{tool.get_name()}"

            msg.Prints.verbose("Try to move the tool", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)

            # Move the tool into the new directory
            errcode = utl_fs.move_file(src_dir, dst_dir)

            if errcode == 1:
                raise click.ClickException(msg.Echoes.error(f"The directory '{new_dir}' already exists!"))
            elif errcode == 3:
                raise click.ClickException(
                    msg.Echoes.error(f"The directory specified: {dst_dir} already exists and is not empty"))
            elif errcode != 0:
                raise click.ClickException(msg.Echoes.error(
                    f"An unexpected error occurred while copying '{new_dir}' directory."))

            msg.Prints.verbose("Tool moved", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)
            msg.Prints.verbose("Setting new tool directory", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)

            # Everything went fine, modify tool's installation directory
            tool.set_directory(new_dir)
            msg.Prints.success("New tool directory set successfully!", cmd_name=CMD_NAME, log_file_name=log_file_name)

            # Save changes
            _save_changes(cfg, tool, vrb, log_file_name)

        else:
            raise click.ClickException(
                msg.Echoes.error(f"The directory '{new_dir}' does not exist or you don't have enough access rights"))

    # Attempt to add one or more tags
    if tag_add:
        msg.Prints.verbose(f"Adding tags to {tool.get_name()}", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)

        tmp_tags = utl_cmd.sanitize_tags(tag_add)
        msg.Prints.verbose(f"Following tags will be added: {tmp_tags}", vrb,
                           cmd_name=CMD_NAME, log_file_name=log_file_name)

        added_tags = []
        for tag in tmp_tags:
            if tag not in tool_tags:
                msg.Prints.verbose(f"Adding tags '{tag}' to {tool.get_name()}", vrb,
                                   cmd_name=CMD_NAME, log_file_name=log_file_name)

                tool_tags.append(tag)
                added_tags.append(tag)

        tool.set_tags(tool_tags)
        msg.Prints.success(f"Following tags have been successfully added: {added_tags}",
                           cmd_name=CMD_NAME, log_file_name=log_file_name)

        # Save changes
        _save_changes(cfg, tool, vrb, log_file_name)

    # Attempt to remove one or more tags
    if tag_rm:
        msg.Prints.verbose(f"Removing tags to {tool.get_name()}", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)

        tmp_tags = utl_cmd.sanitize_tags(tag_rm)
        msg.Prints.verbose(f"Following tags will be removed: {tmp_tags}", vrb,
                           cmd_name=CMD_NAME, log_file_name=log_file_name)

        removed_tags = []
        for tag in tmp_tags:
            if tag in tool_tags:
                msg.Prints.verbose(f"Removing tags '{tag}' to {tool.get_name()}", vrb,
                                   cmd_name=CMD_NAME, log_file_name=log_file_name)

                tool_tags.remove(tag)
                removed_tags.append(tag)

        tool.set_tags(tool_tags)
        msg.Prints.success(f"Following tags have been successfully removed: {removed_tags}"
                           if len(removed_tags) != 0 else "No tags removed",
                           cmd_name=CMD_NAME, log_file_name=log_file_name)

        # Save changes
        _save_changes(cfg, tool, vrb, log_file_name)

    # Attempt to modify a tag
    if tag_mv:
        msg.Prints.verbose(f"Renaming tags of {tool.get_name()}", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)

        old_tag, new_tag = tag_mv
        msg.Prints.verbose(f"Renaming tag {old_tag} to {new_tag}", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)
        msg.Prints.verbose(f"Check if {tool.get_name()} has tag {old_tag}", vrb,
                           cmd_name=CMD_NAME, log_file_name=log_file_name)

        # Make sure the tool has the old tag
        if old_tag in tool_tags:
            msg.Prints.verbose(f"Tool {tool.get_name()} has tag {old_tag}", vrb,
                               cmd_name=CMD_NAME, log_file_name=log_file_name)
            msg.Prints.verbose(f"Check if {tool.get_name()} hasn't already new tag {new_tag}", vrb,
                               cmd_name=CMD_NAME, log_file_name=log_file_name)

            # And make sure the tool has NOT already the new tag
            if new_tag in tool_tags:
                raise click.ClickException(msg.Echoes.error(
                    f"The tool '{tool.get_name()}' already has tag '{new_tag}'."))

            msg.Prints.verbose(f"Attempting to remove tag {old_tag} from {tool.get_name()}", vrb,
                               cmd_name=CMD_NAME, log_file_name=log_file_name)

            tool_tags.remove(old_tag)
            msg.Prints.verbose(f"Old tag {old_tag} removed", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)
            msg.Prints.verbose(f"Attempting to add new tag {new_tag}", vrb,
                               cmd_name=CMD_NAME, log_file_name=log_file_name)

            tool_tags.append(new_tag)
            msg.Prints.verbose(f"New tag {new_tag} added to {tool.get_name()}", vrb,
                               cmd_name=CMD_NAME, log_file_name=log_file_name)
        else:
            raise click.ClickException(msg.Echoes.error(f"The tool '{tool.get_name()}' has no tag '{old_tag}'."))

        tool.set_tags(tool_tags)
        msg.Prints.success(f"{old_tag} tag has been successfully renamed in {new_tag}",
                           cmd_name=CMD_NAME, log_file_name=log_file_name)

        # Save changes
        _save_changes(cfg, tool, vrb, log_file_name)
    sys.exit(0)


def _save_changes(cfg: Config, tool: Tool, vrb: bool, log_file_name: str) -> None:
    """
    Save tool changes.

    :param Config cfg: tman configuration file
    :param Tool tool: tool to save
    :param bool vrb: should print verbose messages?
    :return: None
    """
    msg.Prints.verbose(f"Updating tool {tool.get_name()}...", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)
    cfg.update_tool(tool)
    cfg.save()
    msg.Prints.verbose(f"Tool {tool.get_name()} saved", vrb, cmd_name=CMD_NAME, log_file_name=log_file_name)
