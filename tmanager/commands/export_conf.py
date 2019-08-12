import click
import os
import sys
import zipfile
import tempfile
import time
import tmanager.utilities.file_system as utl_fs
import tmanager.utilities.commands as utl_cmds
import tmanager.core.messages.messages as msg

CMD_NAME = "export_config"


@click.command(short_help="Export configuration file and tools.")
@click.option("-o", "--outfile", help="Config output file.", metavar="<pathname>", required=True)
@click.option("--types", help="Export by types", metavar="[git, local]")
@click.option("--tags", help="Export by tagnames", metavar="t1,t2,t3")
@click.option("-l", "--log", help="Log to file instead of printing to stdout.", metavar="<filename>")
@click.option("-y", "--assume-yes", help="Assume yes.", is_flag=True)
@click.pass_context
def export_conf(ctx: click.core.Context, outfile: str, types: str, tags: str, log: str,
                assume_yes: bool) -> None:
    """
    \b
    Export the configuration as a CSV and optionally compress
    the tools the user wishes to export from the FileSystem.

    \b
    CSV FORMAT:
        - first line contains the list of general properties separated by a comma
        - any other line is a string that represent the involved tool.

    \b
    For instance:
        default_installation_directory-/home/user/.tman/,automatic_install-False
        url-https://github.com/ssh3ll/tmanager,type-git,tags-['t1','t2']
        directory-/home/user/,url--,type-local,tags-['t3','t4']
    \f

    :param click.core.Context ctx: click Context
    :param str outfile: output file path
    :param str types: export by type
    :param str tags: export by tag names
    :param str log: log filename
    :param bool assume_yes: assume yes as the answer for any user prompt
    :return: None
    """
    # if a filename for logs is provided, then make sure it exists and it's writable.
    log_fname = ""
    if log:
        log_fname = utl_cmds.validate_log_filename(log, CMD_NAME, assume_yes)
        if not log_fname:
            sys.exit(1)

    # Retrieve the configuration file if it exists, otherwise start the configuration wizard
    configs = utl_cmds.get_configs_from_context(ctx)

    # Validate outfile pathname
    res = _validate_pathname(outfile, log_fname)

    # File already exists, prompt for overwriting
    if res == 2 and not assume_yes:
        if not click.confirm(msg.Echoes.input(f"Overwrite {outfile} ?"), default=False):
            sys.exit(1)
    # File or directory not writable
    elif res != 0:
        sys.exit(1)

    # if no matching criteria is specified, then prompt the user for choosing tools
    exp_local = exp_all = False
    if not types and not tags:
        exp_all = assume_yes or click.confirm(msg.Echoes.input("Export every tool?"), default=True)
        if not exp_all:
            # Maybe export local tools only?
            exp_local = click.confirm(msg.Echoes.input("Export local tools only?"), default=True)

    # Retrieve the tools that need to be "exported"
    tools_to_export = []
    if types or tags:
        if types and tags:
            tools_to_export = utl_cmds.find_tool(configs, tags=tags, type=types)
        elif types:
            tools_to_export = utl_cmds.find_tool(configs, type=types)
        else:
            tools_to_export = utl_cmds.find_tool(configs, tags=tags)
    elif exp_all:
        tools_to_export = configs.get_tools()
    elif exp_local:
        for t in configs.get_tools():
            if t.is_localfile():
                tools_to_export.append(t)

    # save tot tools
    tot_tools_export = len(tools_to_export)

    # compute temporary filenames
    conf_tmp_fname = f"{tempfile.gettempdir()}/tempconf-{time.time()}.tman"

    # create the zip archive handler
    zip_h = zipfile.ZipFile(outfile, 'w', zipfile.ZIP_DEFLATED)

    # Attempt to export the configuration file as a CSV
    l1 = oth = ""
    with open(conf_tmp_fname, "w") as f:
        for cfg in configs:
            if cfg != "tools":
                # Every non-tool config. parameter goes to the first line
                l1 += f"{cfg}-{configs[cfg]},"

            else:
                # Tools are listed starting from line 2, one per line
                for repo in configs.get_tools():
                    for k in repo.__dict__():
                        if k not in ["install_date", "last_update_date", "add_date"]:
                            # Skip dates
                            oth += f"{k}-{repo.__dict__()[k]},"

                    # Remove last comma and add new-line
                    oth = f"{oth[:-1]}\n"

        # Export the configuration file
        # Remove trailing comma, add \n, and write the first line
        f.write(f"{l1[:-1]}\n")

        # Write the remaining lines, those that represent tools
        f.write(oth)
        msg.Prints.info("Configuration file saved", log_fname, CMD_NAME)

    # add the config file to the archive
    utl_fs.zip_all(zip_h, conf_tmp_fname)

    # Attempt to export the tools
    if tot_tools_export != 0:
        msg.Prints.info(
            f"Compressing {tot_tools_export} {'tool' if tot_tools_export == 1 else 'tools'}, it may take a while..",
            log_fname, CMD_NAME)
        for t in tools_to_export:
            utl_fs.zip_all(zip_h, t.get_directory())

    # close the ZIP file handler
    zip_h.close()
    msg.Prints.success("Archive created successfully", log_fname, CMD_NAME)

    # delete temporary files
    utl_fs.delete_from_fs(conf_tmp_fname)

    sys.exit(0)


def _validate_pathname(filename: str, log_fname: str) -> int:
    """
    Returns True either if the given filename exists and is writable
    OR if it doesn't exist but its parent directory is writable;
    False is returned otherwise.

    Returns 0 if the given filename is allowed,
    otherwise it returns the error codes as described below.

    1 -- file not writable
    2 -- file already exists
    3 -- parent directory not writable

    :param str filename: file name to validate
    :param str log_fname: log filename
    :return int: status code
    """
    # If the file exists, make sure it's writable
    if os.path.isfile(filename) and not utl_fs.is_writable(filename):
        msg.Prints.info(f"The file {filename} is not writable", log_fname, CMD_NAME)
        return 1

    elif os.path.isfile(filename):
        return 2

    # Otherwise make sure it's parent directory is writable
    elif not utl_fs.is_writable(utl_fs.get_parent(filename)):
        msg.Prints.info(f"The directory {utl_fs.get_parent(filename)} is not writable", log_fname, CMD_NAME)
        return 3

    return 0
