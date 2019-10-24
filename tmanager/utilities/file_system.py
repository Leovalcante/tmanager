import os
import platform
import shutil
from typing import Optional

import tmanager.core.messages as msg
from distutils.dir_util import copy_tree


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
