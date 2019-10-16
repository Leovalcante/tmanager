import os
import platform
import shutil
from typing import Optional

import tmanager.core.messages as msg
from distutils.dir_util import copy_tree


def get_home_env() -> str:
    """
    Returns HOME environment variable, depending on the os.

    :return str: HOME or USERPROFILE env var
    """

    if get_os_name() == "win":
        env_var = "USERPROFILE"
    else:
        env_var = "HOME"

    return os.getenv(env_var)


def get_parent(pathname: str) -> str:
    """
    Returns the parent directory of the given pathname.

    :param str pathname: pathname
    :return str: absolute pathname
    """
    return os.path.abspath(os.path.join(pathname, os.pardir))


def get_file_name(pathname: str) -> str:
    """
    Return the last child of the tree represented by the given pathname.

    :param str pathname:
    :return str:
    """
    pathname = pathname.rstrip("/")
    return os.path.basename(pathname)


def trailing_slash(pathname: str) -> str:
    """
    Add a trailing slash if the input pathname is an existing directory and has no trailing slash.

    :param str pathname:
    :return str:
    """
    if os.path.isdir(pathname):
        # Terminate every path representing a directory with a slash
        return os.path.join(pathname, '')

    return pathname


def is_writable(pathname: str) -> bool:
    """
    Returns True if the given file/directory exists and is writable, otherwise returns False.

    :param str pathname:
    :return bool:
    """
    if os.access(pathname, os.W_OK):
        return True

    return False


def is_readable(pathname: str) -> bool:
    """
        Returns True if the given pathname is a readable filename, otherwise returns False.

    :param pathname:
    :return:
    """
    if os.path.isfile(pathname) and os.access(pathname, os.R_OK):
        return True
    return False


def delete_from_fs(pathname: str) -> None:
    """
    Delete a file/directory from the file system.

    :param str pathname:
    :return: None
    """
    if os.path.isdir(pathname):
        shutil.rmtree(pathname, ignore_errors=True)

    else:
        if os.path.exists(pathname):
            os.remove(pathname)


def move_file(src: str, dst: str, rm: bool = True) -> int:
    """
    Copies src into dst
    By default, the src_dir is removed if the copy process succeeds

    :param str src: source directory
    :param str dst: destination directory
    :param bool rm: remove original file Y|N
    :return int: status code:
        - 0: if everything went fine
        - 1: if the destination directory already exists
        - 2: error while moving file
        - 3: file already present
    """
    src = trailing_slash(src)
    dst = trailing_slash(dst)

    if os.path.isdir(src):
        try:
            if src != dst:
                copy_tree(src, dst)
            else:
                return 3

            if rm:
                delete_from_fs(src)  # delete src file
        except FileExistsError:
            msg.Prints.info(f"ERROR - The file {dst} already exists", show_icon=False)
            return 1
    else:
        fname = get_file_name(src)
        try:
            if not dst.endswith(fname):
                shutil.move(src, dst+get_file_name(src))
            else:
                shutil.move(src, dst)
        except shutil.Error:
            return 2
    return 0


def zip_all(zipfh, path: str, rel: str = "") -> None:  # TODO: review zipfh and rel typing
    """
    Recursively compress any file and directory
    that is found under the pathname 'path'.

    :param zipfh: ZIP file handler
    :param path: ZIP pathname
    :param rel:
    :return:
    """
    bname = os.path.basename(path)
    if os.path.isfile(path) and path.endswith(".tman"):
        zipfh.write(path, "conf.tman")
    elif os.path.isdir(path):
        if rel == "":
            rel = bname
        zipfh.write(path, os.path.join(rel))
        for root, dirs, files in os.walk(path):
            for d in dirs:
                zip_all(zipfh, os.path.join(root, d), os.path.join(rel, d))
            for f in files:
                zipfh.write(os.path.join(root, f), os.path.join(rel, f))
            break
    elif os.path.isfile(path):
        zipfh.write(path, os.path.join(rel, bname))
    else:
        pass


def exists_pathname(pathname):
    # TODO: add typing and docstring
    return os.path.exists(pathname)


def get_abs_path(path: str) -> str:
    """
    Get absolute path from given path without the trailing slash.

    :param str path: input non absolute path
    :return str: absolute path
    """
    os_name = get_os_name()

    if os_name == "win":
        return get_abs_path_win(path)
    elif os_name is not None:
        return get_abs_path_unix(path)

    return "None"


def normalize_path(path: str) -> str:
    """
    Normalize given path.

    :param str path: path to be normalized
    :return str: normalized path
    """
    drive = None
    nodes = path.split("/")

    # Check windows drive
    if nodes[0] != "":
        drive = nodes[0]

    directories = []
    nodes = nodes[1:]
    for node in nodes:
        if node == ".":
            continue
        elif node == "..":
            if len(directories) > 0:
                directories.pop()
            else:
                raise Exception("Cannot go beyond base directory")
        else:
            directories.append(node)

    normalized_path = ""
    for directory in directories:
        normalized_path = f"{normalized_path}/{directory}"

    if drive:
        normalized_path = f"{drive}{normalized_path}"

    return normalized_path


def get_abs_path_win(path: str) -> str:
    if path[0] == "/":
        raise Exception("Windows path cannot start with '/' (slash)")
    elif path[0] == "~":
        home_path = get_home_env()
        if home_path is None:
            raise Exception("USERPROFILE env var not set")

        tmp_abs_path = normalize_path(f"{home_path}{path}")
    elif len(path) > 1 and path[1] == ":":
        tmp_abs_path = normalize_path(path)
    else:
        tmp_abs_path = normalize_path(f"{os.getcwd()}/{path}")

    # Invert slashes
    abs_path = ""
    for c in tmp_abs_path:
        if c == "/":
            abs_path += "\\"
        else:
            abs_path = c

    return abs_path


def get_abs_path_unix(path: str) -> str:
    # Remove trailing slashes
    path = path.rstrip("/")

    first_char = path[0]
    if first_char == "/":
        abs_path = normalize_path(path)
    elif first_char == "~":
        home_path = get_home_env()
        if home_path is None:
            raise Exception("HOME env var not set")

        abs_path = normalize_path(f"{home_path}{path[1:]}")
    else:
        abs_path = normalize_path(f"{os.getcwd()}/{path}")

    return abs_path


def get_os_name() -> Optional[str]:
    """
    Get operating system name.

    :return Optional[str]: operating system name: win, mac, linux or None
    """
    platform_name = platform.system().lower()

    os_name = None
    if "windows" in platform_name:
        os_name = "win"
    elif "darwin" in platform_name:
        os_name = "mac"
    elif "linux" in platform_name:
        os_name = "linux"

    return os_name
