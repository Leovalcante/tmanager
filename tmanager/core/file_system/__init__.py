import os
import platform
import shutil
import zipfile
from distutils import dir_util
from typing import Optional

from tmanager.core.messages import Prints


class FileSystem:
    OS_WIN = "win"
    OS_MAC = "mac"
    OS_LINUX = "linux"

    WIN_SLASH = "\\"
    NIX_SLASH = "/"

    @staticmethod
    def get_os_name() -> Optional[str]:
        """
        Get operating system name.

        :return Optional[str]: operating system name: win, mac, linux or None
        """
        platform_name = platform.system().lower()

        os_name = None
        if "windows" in platform_name:
            os_name = FileSystem.OS_WIN
        elif "darwin" in platform_name:
            os_name = FileSystem.OS_MAC
        elif "linux" in platform_name:
            os_name = FileSystem.OS_LINUX

        return os_name

    @staticmethod
    def get_home_env() -> Optional[str]:
        """
        Returns HOME environment variable, depending on the os.

        :return Optional[str]: HOME env var depending on the system
        """
        os_name = FileSystem.get_os_name()
        env_var = None

        if os_name == FileSystem.OS_WIN:
            env_var = "USERPROFILE"
        elif os_name in (FileSystem.OS_LINUX, FileSystem.OS_MAC):
            env_var = "HOME"

        home_path = os.getenv(env_var) if env_var is not None else None

        return home_path

    @staticmethod
    def get_abs_path(path: str, trailing_slash: bool = False) -> Optional[str]:
        """
        Get absolute path from given path without the trailing slash.

        :param str path: non absolute path
        :param bool trailing_slash: should append trailing slash
        :return Optional[str]: absolute path
        """
        # TODO: this substitute trailing_slash using option trailing_slash = True
        os_name = FileSystem.get_os_name()
        abs_path = None

        if os_name == "win":
            abs_path = FileSystem.get_abs_path_win(path, trailing_slash)
        elif os_name in ("mac", "linux"):
            abs_path = FileSystem.get_abs_path_unix(path, trailing_slash)

        return abs_path

    @staticmethod
    def get_abs_path_win(path: str, trailing_slash: bool) -> str:
        """
        Return windows absolute path.

        :param str path: not absolute path
        :param bool trailing_slash: should append trailing slash
        :return str: absolute path
        """
        if path[0] == FileSystem.NIX_SLASH:
            raise Exception(f"Windows path cannot start with '{FileSystem.NIX_SLASH}' (slash)")
        elif path[0] == "~":
            home_path = FileSystem.get_home_env()
            if home_path is None:
                raise Exception("USERPROFILE env var not set")

            tmp_abs_path = FileSystem.get_normalized_path(f"{home_path}{path}")
        elif len(path) > 1 and path[1] == ":":
            tmp_abs_path = FileSystem.get_normalized_path(path)
        else:
            tmp_abs_path = FileSystem.get_normalized_path(f"{os.getcwd()}{FileSystem.NIX_SLASH}{path}")

        # Invert slashes
        abs_path = FileSystem.invert_slashes(tmp_abs_path, FileSystem.WIN_SLASH)

        if trailing_slash and os.path.isdir(abs_path):
            abs_path += FileSystem.WIN_SLASH

        return abs_path

    @staticmethod
    def get_normalized_path(path: str) -> str:
        """
        Normalize given path.

        :param str path: path to be normalized
        :return str: normalized path
        """
        drive = None
        nodes = path.split(FileSystem.NIX_SLASH)

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
            normalized_path = f"{normalized_path}{FileSystem.NIX_SLASH}{directory}"

        if drive:
            normalized_path = f"{drive}{normalized_path}"

        return normalized_path

    @staticmethod
    def invert_slashes(path: str, slash: str = NIX_SLASH) -> str:
        """
        TODO

        :param path:
        :param slash:
        :return:
        """
        new_path = ""
        for path_char in path:
            if path_char in (FileSystem.NIX_SLASH, FileSystem.WIN_SLASH):
                new_path += slash
            else:
                new_path += path_char

        return new_path

    @staticmethod
    def get_abs_path_unix(path: str, trailing_slash: bool) -> str:
        """
        Return linux absolute path.

        :param str path: not absolute path
        :param bool trailing_slash: should append trailing slash
        :return str: absolute path
        """
        # Remove any trailing slashes
        path = path.rstrip(FileSystem.NIX_SLASH)

        first_char = path[0]
        if first_char == FileSystem.NIX_SLASH:
            abs_path = FileSystem.get_normalized_path(path)
        elif first_char == "~":
            home_path = FileSystem.get_home_env()
            if home_path is None:
                raise Exception("HOME env var not set")

            abs_path = FileSystem.get_normalized_path(f"{home_path}{path[1:]}")
        else:
            abs_path = FileSystem.get_normalized_path(f"{os.getcwd()}{FileSystem.NIX_SLASH}{path}")

        if trailing_slash and os.path.isdir(abs_path):
            abs_path += FileSystem.NIX_SLASH

        return abs_path

    @staticmethod
    def get_parent_directory(path: str) -> str:
        """
        Get the parent directory of the given path.

        :param str path: full path
        :return str: path parent directory
        """
        # TODO: this substitute get_parent
        abs_path = FileSystem.get_abs_path(path)
        return os.path.dirname(abs_path)

    @staticmethod
    def get_basename(path: str) -> str:
        """
        Get the path basename.

        :param str path: full path
        :return str: path basename
        """
        # TODO: this substitute get_file_name
        abs_path = FileSystem.get_abs_path(path)
        return os.path.basename(abs_path)

    @staticmethod
    def does_path_exist(path: str) -> bool:
        """
        Check if the given path exists or not.

        :param str path: path to check
        :return bool: True if path exists, False otherwise
        """
        # TODO: substitute exists_pathname
        abs_path = FileSystem.get_abs_path(path)
        return os.path.exists(abs_path)

    @staticmethod
    def is_path_readable(path: str) -> bool:
        """
        Check if path is readable.

        :param str path: path to check
        :return bool: True if path is readable, False otherwise
        """
        # TODO: substitute is_readable
        abs_path = FileSystem.get_abs_path(path)
        return os.access(abs_path, os.R_OK)

    @staticmethod
    def is_path_writable(path: str) -> bool:
        """
        Check if path is writable.

        :param str path: path to check
        :return bool: True if path is writable, False otherwise
        """
        # TODO: substitute is_writable
        abs_path = FileSystem.get_abs_path(path)
        return os.access(abs_path, os.W_OK)

    @staticmethod
    def delete(path: str) -> None:
        """
        Delete a file or a directory from the file system.

        :param str path: path to delete
        :return: None
        """
        # TODO: substitute delete_from_fs
        # TODO: manage exceptions
        abs_path = FileSystem.get_abs_path(path)
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path, ignore_errors=True)
        elif os.path.exists(abs_path):
            os.remove(abs_path)

    @staticmethod
    def move(src: str, dst: str, delete: bool = True) -> int:
        """
        Copies src into dst, if delete is True after the copy src is removed.

        :param str src: source file or directory
        :param str dst: destination file or directory
        :param bool delete: remove the source file
        :return int: status code:
            - 0: everything went fine
            - 1: destination file or directory already exists
            - 2: error while moving file or directory
            - 3: file or directory not moved: source == destination
        """
        # TODO: substitute move_file
        abs_src = FileSystem.get_abs_path(src, trailing_slash=True)
        abs_dst = FileSystem.get_abs_path(dst, trailing_slash=True)

        # Check if source and destination are not the same
        if abs_src == abs_dst:
            return 3

        # Check if source is a directory
        if os.path.isdir(abs_src):
            try:
                # Copy the directory or the file
                dir_util.copy_tree(abs_src, abs_dst)  # TODO: can this be done using shutil?

                # Remove it if necessary
                if delete:
                    FileSystem.delete(abs_src)
            except FileExistsError:  # TODO: review this catch, we may have missed some exceptions
                Prints.info(f"ERROR: The file {dst} already exists!")
                return 1

        else:  # We are moving a file
            # Get the file basename
            file_name = FileSystem.get_basename(abs_src)

            destination = abs_dst if abs_dst.endswith(file_name) else abs_dst + file_name
            # Try to move the file
            try:
                shutil.move(abs_src, destination)
            except shutil.Error:
                return 2

        return 0

    @staticmethod
    def zip(zip_handler: zipfile.ZipFile, path: str, rel: Optional[str] = None) -> None:
        """
        Recursively compress any file and/or directory that is found under path.

        :param zipfile.ZipFile zip_handler: zipfile handler
        :param str path: path to compress
        :param str rel: TODO: what is this???
        :return: None
        """
        # TODO: ex zip_all
        abs_path = FileSystem.get_abs_path(path)
        basename = FileSystem.get_basename(abs_path)

        if rel is None:
            rel = basename

        if os.path.isfile(abs_path):
            if abs_path.endswith(".tman"):
                zip_handler.write(abs_path, "conf.tman")
            else:
                zip_handler.write(path, os.path.join(rel, basename))

        elif os.path.isdir(abs_path):
            zip_handler.write(path, os.path.join(rel))

            for root, dirs, files in os.walk(path):
                for d in dirs:
                    FileSystem.zip(zip_handler, os.path.join(root, d), os.path.join(rel, d))

                for f in files:
                    zip_handler.write(os.path.join(root, f), os.path.join(rel, f))

                break  # TODO: can this break be replaced?
