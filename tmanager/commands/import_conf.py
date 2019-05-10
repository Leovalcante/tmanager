import click
import os
import sys
import time
import zipfile
import tempfile
import tmanager.utilities.file_system as utl_fs
import tmanager.utilities.commands as utl_cmds
import tmanager.core.messages.messages as msg
from tmanager.core.config.config import Config
from tmanager.core.tool.repository.repository import Repository
from tmanager.core.tool.localfile.localfile import LocalFile

CMD_NAME = "import_config"


@click.command(short_help="Import configuration file and tools.")
@click.option("-i", "--infile", help="Input configuration file.", metavar="<pathname>", required=True)
@click.option("--types", help="Import by types.", metavar="[git, local]")
@click.option("--tags", help="Import by tag names.", metavar="t1,t2,t3")
@click.option("-l", "--log", help="Log to file instead of printing to stdout.", metavar="<filename>")
@click.option("-y", "--assume_yes", help="Assume yes.", is_flag=True)
@click.pass_context
def import_conf(ctx: click.core.Context, infile: str, types: str, tags: str, log: str, assume_yes: bool) -> None:
    """
    \b
    Import a configuration file (previously exported through tman)
    and allow to import an archive containing the tools.

    \b
    Examples:
        1 - import tman configuration file only
            tman --import-conf /home/user/tman-config.csv
        2 - import a configuration file AND the content of a compressed file
            tman --import-conf /home/user/tman-config.csv:/home/user/mytools.zip
    \f

    :param click.core.Context ctx: click context
    :param str infile: input configuration file
    :param str types: export by type names
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

    # Validate input types and input tags (if any)
    import_types = set()
    if types:
        for t in types.split(","):
            t = t.strip()
            if t in ["git", "local"]:
                import_types.add(t)
    import_types = list(import_types)
    import_tags = utl_cmds.sanitize_tags(tags)

    # Validate input filename
    if not utl_fs.is_writable(infile):
        msg.Prints.info("'{}' does not exist or it's just not writable".format(infile), log_fname, CMD_NAME)
        sys.exit(1)

    # Attempt to load the configuration file
    new_cfg = Config()
    if new_cfg.load(importing=True) == 1:
        # Create the default installation directory if it doesn't exist
        msg.Prints.info("Configuration file not found", log_fname, CMD_NAME)
        new_cfg.first_configuration(importing=True)

    # Attempt to open the ZIP archive
    zip_h = None
    try:
        zip_h = zipfile.ZipFile(infile, 'r')
    except zipfile.BadZipFile:
        msg.Prints.info("The file '{}' doesn't seem a ZIP archive".format(infile), log_fname, CMD_NAME)
        if zip_h:
            zip_h.close()
        sys.exit(1)

    # Detect the configuration file and quit if none is found
    try:
        zip_h.getinfo("conf.tman")
        has_conf = True
    except KeyError:
        has_conf = False

    if not has_conf:
        msg.Prints.info("No configuration file detected, quitting..".format(infile), log_fname, CMD_NAME)
        sys.exit(1)

    # Retrieve tools from the archive (if any)
    tools_to_import = set()
    for t in zip_h.namelist():
        if t != "conf.tman":
            tools_to_import.add(t.split("/", 1)[0])
    tools_to_import = list(tools_to_import)

    # Retrieve current file/tools
    managed_tools = new_cfg.get_tools()

    # Unzip the input file into
    tmp_dir = "{}/export-{}".format(tempfile.gettempdir(), int(time.time()))
    zip_h.extractall(tmp_dir)

    # Attempt to import the configuration file ONLY
    if len(tools_to_import) == 0:
        _import_conf_file(managed_tools, new_cfg, "{}/{}".format(tmp_dir, "conf.tman"), assume_yes, log_fname,
                          import_types=import_types if types else None, import_tags=import_tags if tags else None)

    else:
        msg.Prints.info("Importing tools, this may take a while..", log_fname, CMD_NAME)
        _import_conf_file(managed_tools, new_cfg, "{}/{}".format(tmp_dir, "conf.tman"), assume_yes, log_fname,
                          import_types=import_types if types else None, import_tags=import_tags if tags else None)
        _import_tools_from_archive(new_cfg, "{}{}".format(tmp_dir, "/" if not tmp_dir.endswith("/") else ""),
                                   assume_yes, log_fname, import_types=import_types if types else None,
                                   import_tags=import_tags if tags else None)

    # Auto_install if required
    new_cfg.auto_install()

    # delete temp files
    utl_fs.delete_from_fs(tmp_dir)

    # close the handler
    if zip_h:
        zip_h.close()

    sys.exit(0)


def _import_conf_file(all_tools: list, new_cfg: Config, input_conf: str, assume_yes: bool, log_fname: str,
                      import_types: list = None, import_tags: list = None) -> None:
    """
    Attempt to import a tman configuration file.

    :param list all_tools: tool list
    :param Config new_cfg: configuration object
    :param str input_conf: input configuration file
    :param bool assume_yes: assume YES for any user prompt
    :param str log_fname: log filename
    :return: None
    """
    # Parse the tman configuration file and import the configuration
    b = False
    with open(input_conf, "r") as f:
        for line in f.readlines():
            line = line.strip()
            match_type = True
            match_tag = False
            if not b:
                # First line: general configurations
                b = True
                for val in line.split(","):
                    r = val.split("-", 1)
                    if r[1] in ["True", "False"]:
                        # Convert JSON "True/False" into True/False
                        r[1] = True if r[1] == "True" else False

                    # Set the property
                    new_cfg[r[0]] = r[1]

            else:
                # Other line: Tool representation
                dict_repo = {}
                line, tags = utl_cmds.remove_tags(line)

                # skip tools that have no matching tag name
                if import_tags:
                    for tag in tags:
                        if tag in import_tags:
                            match_tag = True
                            break
                    if not match_tag:
                        continue

                dict_repo["tags"] = tags

                # Create a dictionary representing a tool
                for prop in line.split(","):
                    if prop == '':
                        continue

                    # Parse tool's property
                    res = prop.split("-", 1)

                    # skip tools that don't match types criteria
                    if res[0] == "type" and (import_types is not None and res[1] not in import_types):
                        match_type = False
                        break

                    # Add tool property
                    dict_repo[res[0]] = res[1]

                # skip tools with bad type
                if not match_type:
                    continue

                # Instantiates a new Tool
                if dict_repo["url"] == "-":
                    if os.path.exists(dict_repo["directory"]):
                        tool = LocalFile(dict_repo["directory"], tags=tags, add_date=time.time())

                    else:
                        tool = LocalFile(dict_repo["directory"], tags=tags, add_date=time.time())

                else:
                    tool = Repository(dict_repo["url"], dict_repo["directory"], name=dict_repo["name"], tags=tags,
                                      add_date=time.time())

                # Add the tool if it's not None nor already managed
                if tool is not None:
                    if all_tools.__contains__(tool):
                        # If the tool is already managed, then prompt confirmation
                        if assume_yes or click.confirm(msg.Echoes.input("{} is already managed, overwrite "
                                                                        "its configuration?".format(tool.get_name())),
                                                       default=True):
                            new_cfg.update_tool(tool)

                    else:
                        new_cfg.add_tool(tool)

                    new_cfg.save()

    new_cfg.save()
    msg.Prints.info("Configuration file saved", log_fname, CMD_NAME)


def _import_tools_from_archive(new_cfg: Config, tmp_dir: str, assume_yes: bool, log_fname: str,
                               import_types: list = None, import_tags: list = None) -> None:
    """
    Import tools from archive.

    :param Config new_cfg: tman configuration object
    :param str tmp_dir: temporary directory for extracting the archive
    :param bool assume_yes: should assume all positive answers to any confirmation prompt?
    :return: None
    """

    # Retrieve file names contained into the compressed file
    files = os.listdir(tmp_dir)

    # Compute their absolute pathnames
    abs_name = [tmp_dir + f for f in files]

    # Add every tool that is not managed
    temp = new_cfg.get_tools()

    # For any tool t
    tot_imported = 0
    for t in temp:
        # And for any computed absolute pathname absf
        for absf in abs_name:
            # If name matches, then try to copy it (also ensure that the tool matches any tag/type that is provided)
            if t.get_name() == utl_fs.get_file_name(absf) and (not import_types or t.get_type() in import_types):
                if import_tags:
                    match_tags = False
                    for tag in t.get_tags():
                        if tag in import_tags:
                            match_tags = True
                            break
                    # skip tools that have no matching tag name
                    if not match_tags:
                        continue
                if os.path.exists(t.get_directory()):
                    # Prompt for action if the file already exists
                    if assume_yes or click.confirm(msg.Echoes.input("{} already exists, overwrite?".format(
                            t.get_directory())), default=False):
                        if utl_fs.move_file(tmp_dir + utl_fs.get_file_name(absf), t.get_directory()) == 0:
                            msg.Prints.success("{} replaced".format(t.get_directory()), log_fname, CMD_NAME)
                            tot_imported += 1

                else:
                    # Move the file it doesn't yet exist
                    utl_fs.move_file(tmp_dir + utl_fs.get_file_name(absf), t.get_directory())
                    tot_imported += 1

                break

    if tot_imported != 0:
        msg.Prints.success("tools imported properly", log_fname, CMD_NAME)

    utl_fs.delete_from_fs(tmp_dir)
    new_cfg.save()


def _validate_format(format_val: str, log_fname: str) -> str:
    # set it to its default value if it's not provided
    if not format_val:
        return "zip"
    # otherwise make sure it's valid
    elif format_val not in ["zip"]:
        msg.Prints.info("The format '{}' is not supported".format(format_val), log_fname, CMD_NAME, icon=True)
        sys.exit(1)
