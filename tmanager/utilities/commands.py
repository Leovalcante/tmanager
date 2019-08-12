import click
import os
import tmanager.core.messages.messages as msg
import tmanager.utilities.file_system as utl_fs
from srblib import abs_path
from tmanager.core.config.config import Config


def find_tool(cfg: Config, url: str = None, tags: str = None, name: str = None, type: str = None,
              last_update_date: str = None, f: bool = False) -> list:
    """
    Returns the list of Tools that match all the provided input criteria.

    :param Config cfg: configurations object
    :param str url: repository url
    :param str tags: repository tags
    :param str name: repository name
    :param str type: repository type
    :param str last_update_date: repository last_update_date
    :param bool f: flexible find
    :return list: repositories list
    """
    found_tools = []
    tools = cfg.get_tools()

    # sanitize tags list
    tags = sanitize_tags(tags)

    if url is not None:
        url = url if url.endswith(".git") else f"{url}.git"

    search_terms = {
        "url": url,
        "tags": tags,
        "name": name,
        "type": type,
        "last_update_date": last_update_date
    }

    # The only tools that are returned are those that match all the search terms
    for tool in tools:
        is_url_ok = is_tags_ok = is_name_ok = is_type_ok = is_last_update_date_ok = True

        for key in search_terms:
            if search_terms[key]:
                # Check if the tool's url matches the input url
                if key == "url":
                    if tool.get_url() not in search_terms["url"]:
                        is_url_ok = False

                # Check if the tool has any matching tags
                elif key == "tags":
                    if not set([x.lower() for x in search_terms["tags"]]).issubset(set(y.lower() for y in
                                                                                       tool.get_tags())):
                        is_tags_ok = False

                # Check if the tool's name matches
                elif key == "name":
                    toolname = tool.get_name()
                    # if flexible find flag is set
                    if f:
                        found = False
                        for t in search_terms["name"]:
                            if toolname.lower() == t.lower() or t.lower() in toolname.lower():
                                found = True
                                break
                        if not found:
                            is_name_ok = False

                    elif toolname not in search_terms["name"]:
                        is_name_ok = False

                # Check if the tool's type matches
                elif key == "type":
                    if tool.get_type() not in search_terms["type"]:
                        is_type_ok = False

                # Check if tool's last_update_date is >= searched__last_update_date
                elif key == "last_update_date":
                    if tool.get_last_update_date() is None \
                            or tool.get_last_update_date() < search_terms["last_update_date"]:
                        is_last_update_date_ok = False

        # If everything is True then add the repository
        if is_url_ok and is_tags_ok and is_name_ok and is_type_ok and is_last_update_date_ok:
            found_tools.append(tool)

    return found_tools


def sanitize_indexes(indexes: list, user_input: str) -> list:
    """
    Given a list of valid indexes and a comma-separated
    string of (supposedly) user-entered indexes,
    it returns the list of indexes that are valid.

    :param list indexes: list of permitted indexes
    :param str user_input: comma-separated list of ind.
    :return list: list of valid indexes
    """
    res = set()
    max_val = len(indexes)

    for index in user_input.split(","):
        index = index.strip()
        if index.isdigit() and int(index)-1 < max_val:
            res.add(int(index)-1)
    return list(res)


def is_git_url(url: str) -> bool:
    """
    Check whether given url is a possible git URL.
    It then returns True when the given URL is a possible git URL
    and returns False otherwise.

    :param str url: url to check
    :return: True if url could be a git url, False otherwise
    """
    # TODO: make this controls more restrictive
    if url.startswith("http") or url.startswith("git"):
        return True

    return False


def sanitize_types(types: str) -> list:
    valid_types = []
    types = types.split(",")
    for t in types:
        if t in ["git", "local"] and t not in valid_types:
            valid_types.append(t)
    return valid_types


def sanitize_tags(tags: str) -> list:
    """
    Given a tag list (represented as the input string 'tags') it returns
    a list containing valid and sanitized tags.

    **Note that:
        - tags cannot contain spaces
        - this method might return an empty list

    :param str tags: tag string to sanitize
    :return list: sanitized tags
    """
    valid_tags = []
    if tags:
        if type(tags) is not list:
            tags = tags.split(",")
        for tag in tags:
            # remove spaces
            tag = tag.strip().replace(" ", "")
            if tag:
                valid_tags.append(tag)
    return valid_tags


def remove_tags(line: str) -> (str, list):
    """
    Given a CSV-like tool string, returns a tuple (string, list)
    where list is a Python list representing the identified tags
    and string is the original string without the tags part.

    :param str line:
    :return tuple:
    """
    tags = []
    start = line.find("tags-[")
    end = -1
    # Parse each tag
    for i in range(start, len(line)):
        if line[i] == "]":
            end = i

    tag_str = line[start:end + 1]
    line_without_tags = line.replace(tag_str, "")

    for t in [k.strip()[1:-1] for k in tag_str.split("-", 1)[1][1:-1].split(",")]:
        if t is not None and t != '':
            tags.append(t)

    return line_without_tags, tags


def get_configs_from_context(ctx: click.core.Context) -> Config:
    """
    Return configuration object from context

    :param click.core.Context ctx: click context
    :return Config: configuration
    """
    return ctx.obj["configurations"]


def get_verbose_from_context(ctx: click.core.Context) -> bool:
    """
    Return verbose flag from context

    :param click.core.Context ctx: click context
    :return bool: verbose flag
    """
    return ctx.obj["verbose"]


def _make_it_list(args: list) -> list:
    """
    Make it list return all args element as list in a list.

    :param list args: list of the argument to return as list
    :return list: list of the args that are now list
    """
    r = []
    for x in args:
        if x is None:
            r.append([])

        elif not isinstance(x, list):
            r.append(list(x))

        else:
            r.append(x)

    return r


def usage_error(cmd_name):
    msg.Prints.info("Usage error: tman [OPTIONS] command [ARGS]")
    msg.Prints.info(f"Run 'tman {cmd_name} --help' to see options", icon=False)


def validate_log_filename(filename: str, cmd_name: str, assume_yes: bool = False) -> str:
    """
    Returns the absolute pathname of the filename given as input
    if the file exists, is writable, and the user wishes to overwrite it
    OR
    if the file doesn't exist but is created successfully.
    :param filename:
    :param cmd_name:
    :param bool assume_yes: overwrite the input file without asking the user
    :return:
    """
    log_fname = ""

    # if it's a writable file then retrieve the logfile absolute pathname
    if utl_fs.is_writable(filename) and os.path.isfile(filename):
        if not assume_yes and not click.confirm(f"'{filename}' exists, overwrite?"):
            return log_fname
        log_fname = abs_path(filename)
    # if it's not writable or it doesn't exist or it's a directory, then quit
    elif os.path.exists(filename):
        msg.Prints.warning(f"file {filename} doesn't exist or it's not writable", log_fname, cmd_name)
        return log_fname
    # attempt to create the new log file
    else:
        try:
            with open(filename, "w"):
                pass
        except PermissionError:
            msg.Prints.warning(f"not enough privileges to create {filename}", log_fname, cmd_name)
            return log_fname
        except FileNotFoundError:
            msg.Prints.warning("please enter a valid pathname", log_fname, cmd_name)
            return log_fname
        log_fname = abs_path(filename)

    return log_fname


def get_user_login() -> str:
    """
    Check user uid and return user name

    :return str: user name
    """
    return "root" if os.getuid() == 0 else os.getlogin()
