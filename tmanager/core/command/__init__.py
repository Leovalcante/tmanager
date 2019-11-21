import os
import time
from abc import ABC, abstractmethod
from typing import Optional

import click

from tmanager.core.config import Config
from tmanager.core.file_system import FileSystem
from tmanager.core.messages import Echoes


class AbstractCommand(ABC):
    """Base command class."""
    def __init__(self, name: str, name_desc: str, version: str) -> None:
        """
        Initialize command.

        :param str name: command name
        :param str name_desc: descriptive command name
        :param str version: command version
        :return: None
        """
        self.name = name
        self.name_desc = name_desc
        self.version = version
        self.config = None

    @abstractmethod
    def exec(self, *args) -> None:
        """
        Execute command.

        :param args: command arguments
        :return: None
        """
        pass

    @staticmethod
    def get_config_from_context(ctx: click.core.Context) -> Optional[dict]:
        """
        Get tmanager configuration from click context.

        :param click.core.Context ctx: click context
        :return Optional[dict]: tmanager configuration
        """
        return ctx.obj.get("config")

    @staticmethod
    def get_default_log_file_path() -> str:
        """
        Return default log file path.

        :return str: default log file path
        """
        return f"{Config().config_dir}/{time.time()}.log"

    @staticmethod
    def validate_log_file(log_file: str, assume_yes: bool = False) -> str:
        """
        Validate log file.

        :param log_file: file to validate
        :param assume_yes: if True bypass confirmation using Yes as answer
        :return str: absolute path of the log file
        """
        abs_log_file_path = FileSystem.get_abs_path(log_file)
        should_overwrite = None
        # File exists and it's writable
        if os.path.isfile(abs_log_file_path) and FileSystem.is_path_writable(abs_log_file_path):
            # Ask for overwrite if not assume yes
            should_overwrite = assume_yes or click.confirm(
                f"{abs_log_file_path} already exists, do you want to overwrite it", prompt_suffix="?")

        # If log file exists or it isn't writable
        elif os.path.exists(abs_log_file_path):
            if os.path.isdir(abs_log_file_path):
                raise click.UsageError(Echoes.error("Please specify a correct path"))
            else:
                raise click.UsageError(Echoes.error(f"Not enough privilege to create/write {abs_log_file_path}"))

        # Attempt to create the file if it doesn't exists or user wants to overwrite it
        if should_overwrite is not False:
            try:
                with open(abs_log_file_path, "w"):
                    pass
            except PermissionError:
                raise click.UsageError(Echoes.error(f"Not enough privilege to create/write {abs_log_file_path}"))
            except FileNotFoundError:
                raise click.UsageError(Echoes.error("Please enter a valid log file name"))
        else:
            raise click.UsageError(Echoes.error(f"File {abs_log_file_path} already exists"))

        return abs_log_file_path

    @staticmethod
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
            tags = tags.split(",")
            for tag in tags:
                # Remove spaces
                tag = tag.replace(" ", "")
                if tag:
                    valid_tags.append(tag)

        return valid_tags
