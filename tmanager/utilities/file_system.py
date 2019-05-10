import os
import shutil
import tmanager.core.messages.messages as msg
from distutils.dir_util import copy_tree


def get_home_env() -> str:
    """
    Returns $HOME environment variable

    :return str: HOME env var
    """
    return os.getenv("HOME")


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
            msg.Prints.info("ERROR - The file {} already exists".format(dst), "", "", icon=False)
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


def zip_all(zipfh, path: str, rel: str = "") -> None:
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
    return os.path.exists(pathname)
