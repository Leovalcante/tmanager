import datetime
from typing import Optional

import click

ICON_ERROR = "[-]"
ICON_SUCCESS = "[+]"
ICON_ALERT = "[!]"
ICON_INFO = "[*]"

LOG_VERBOSE = "VERBOSE"
LOG_INFO = "INFO"
LOG_WARNING = "WARNING"
LOG_ERROR = "ERROR"

COLOR_ERROR = "red"
COLOR_WARNING = "yellow"
COLOR_SUCCESS = "green"
COLOR_INFO = "white"
COLOR_INPUT = "blue"
COLOR_VERBOSE = "magenta"


class Prints:
    @staticmethod
    def log_to_file(msg: str, log_level: str, cmd_name: str, log_file: str) -> None:
        """
        Log the message to the file log_file.
        The log strings have the format specified below.

            yyyy/mm/gg hh:mm:ss | cmd_name | log_level | msg

        :param str msg: message to print
        :param str log_level: logging level
        :param str cmd_name: command that produce the log
        :param str log_file: file where to write
        :return: None
        """
        now = datetime.datetime.now()
        date_time = f"{now.year}-{now.month}-{now.day} {now.hour}:{now.minute}:{now.second}"

        # Compute the log string:  date_time | cmd_name | log_level | msg
        msg = msg.replace("\n", "--")
        log_str = f"{date_time} | {cmd_name} | {log_level} | {msg}\n"

        # Write the string to file
        with open(log_file, "a") as f:
            f.write(log_str)

    @staticmethod
    def print(msg: str, icon: str, color: str, show_icon: Optional[bool] = True,
              bold: Optional[bool] = False, log_file: Optional[str] = None,
              log_level: Optional[str] = None, cmd_name: Optional[str] = None) -> None:
        """
        Print message or log it into file.

        :param str msg: message to print
        :param str icon: icon to print
        :param str color: text color
        :param Optional[bool] show_icon: should show icon?
        :param Optional[bool] bold: should text be in bold format?
        :param Optional[str] log_file: log file name
        :param Optional[str] log_level: log severity
        :param Optional[str] cmd_name: command name that produces the log
        :return: None
        """
        if log_file is not None:
            Prints.log_to_file(msg, log_level, cmd_name, log_file)
        else:
            if not show_icon:
                icon = ""
            else:
                icon += " "  # Add a space after the icon

            click.echo(click.style(f"{icon}{msg}", fg=color, bold=bold))

    @staticmethod
    def error(msg: str, show_icon: Optional[bool] = True,
              cmd_name: Optional[str] = None, log_file: Optional[str] = None) -> None:
        """
        Print error messages.

        :param str msg: message to print
        :param Optional[bool] show_icon: should show message icon
        :param Optional[str] cmd_name: command name
        :param Optional[str] log_file: log filename
        :return: None
        """
        Prints.print(msg=msg, icon=ICON_ERROR, color=COLOR_ERROR, show_icon=show_icon, bold=True,
                     log_file=log_file, log_level=LOG_ERROR, cmd_name=cmd_name)

    @staticmethod
    def warning(msg: str, show_icon: Optional[bool] = True,
                cmd_name: Optional[str] = None, log_file: Optional[str] = None) -> None:
        """
        Print warning messages.

        :param str msg: message to print
        :param Optional[bool] show_icon: should show message icon
        :param Optional[str] cmd_name: command name
        :param Optional[str] log_file: log filename
        :return: None
        """
        Prints.print(msg=msg, icon=ICON_ALERT, color=COLOR_WARNING, show_icon=show_icon, bold=True,
                     log_file=log_file, log_level=LOG_WARNING, cmd_name=cmd_name)

    @staticmethod
    def success(msg: str, show_icon: Optional[bool] = True,
                cmd_name: Optional[str] = None, log_file: Optional[str] = None) -> None:
        """
        Print success messages.

        :param str msg: message to print
        :param Optional[bool] show_icon: should show message icon
        :param Optional[str] cmd_name: command name
        :param Optional[str] log_file: log filename
        :return: None
        """
        Prints.print(msg=msg, icon=ICON_SUCCESS, color=COLOR_SUCCESS, show_icon=show_icon,
                     log_file=log_file, log_level=LOG_INFO, cmd_name=cmd_name)

    @staticmethod
    def info(msg: str, show_icon: Optional[bool] = True,
             cmd_name: Optional[str] = None, log_file: Optional[str] = None) -> None:
        """
        Print info messages.

        :param str msg: message to print
        :param Optional[bool] show_icon: should show message icon
        :param Optional[str] cmd_name: command name
        :param Optional[str] log_file: log filename
        :return: None
        """
        Prints.print(msg=msg, icon=ICON_INFO, color=COLOR_INFO, show_icon=show_icon,
                     log_file=log_file, log_level=LOG_INFO, cmd_name=cmd_name)

    @staticmethod
    def input(msg: str, show_icon: Optional[bool] = True) -> None:
        """
        Print input messages.

        :param str msg: message to print
        :param Optional[bool] show_icon: should show message icon
        :return: None
        """
        Prints.print(msg=msg, icon=ICON_INFO, color=COLOR_INPUT, show_icon=show_icon)

    @staticmethod
    def verbose(msg: str, verbose: bool, show_icon: Optional[bool] = True,
                cmd_name: Optional[str] = None, log_file: Optional[str] = None) -> None:
        """
        Print verbose messages.

        :param str msg: message to print
        :param bool verbose: should print the message?
        :param Optional[bool] show_icon: should show message icon
        :param Optional[str] cmd_name: command name
        :param Optional[str] log_file: log filename
        :return: None
        """
        if verbose:
            Prints.print(msg=msg, icon=ICON_INFO, color=COLOR_VERBOSE, show_icon=show_icon,
                         log_file=log_file, log_level=LOG_VERBOSE, cmd_name=cmd_name)


class Echoes:
    @staticmethod
    def return_message(msg: str, icon: str, color: str,
                       show_icon: Optional[bool] = True, bold: Optional[bool] = False) -> str:
        """
        Return formatted message.

        :param str msg: message to print
        :param str icon: icon to print
        :param str color: text color
        :param Optional[bool] show_icon: should show icon?
        :param Optional[bool] bold: should text be in bold format?
        :return str: formatted message
        """
        if not show_icon:
            icon = ""
        else:
            icon += " "  # Add a space after the icon

        return click.style(f"{icon}{msg}", fg=color, bold=bold)

    @staticmethod
    def error(msg: str, show_icon: Optional[bool] = True) -> str:
        """
        Print error messages.

        :param str msg: message to print
        :param Optional[bool] show_icon: should show message icon
        :return str: colored error message
        """
        return Echoes.return_message(msg=msg, icon=ICON_ERROR, color=COLOR_ERROR, show_icon=show_icon, bold=True)

    @staticmethod
    def warning(msg: str, show_icon: Optional[bool] = True) -> str:
        """
        Print warning messages.

        :param str msg: message to print
        :param Optional[bool] show_icon: should show message icon
        :return str: colored warning message
        """
        return Echoes.return_message(msg=msg, icon=ICON_ALERT, color=COLOR_WARNING, show_icon=show_icon, bold=True)

    @staticmethod
    def success(msg: str, show_icon: Optional[bool] = True) -> str:
        """
        Print success messages.

        :param str msg: message to print
        :param Optional[bool] show_icon: should show message icon
        :return str: colored success message
        """
        return Echoes.return_message(msg=msg, icon=ICON_SUCCESS, color=COLOR_SUCCESS, show_icon=show_icon)

    @staticmethod
    def info(msg: str, show_icon: Optional[bool] = True) -> str:
        """
        Print info messages.

        :param str msg: message to print
        :param Optional[bool] show_icon: should show message icon
        :return str: colored info message
        """
        return Echoes.return_message(msg=msg, icon=ICON_INFO, color=COLOR_INFO, show_icon=show_icon)

    @staticmethod
    def input(msg: str, show_icon: Optional[bool] = True) -> str:
        """
        Print input messages.

        :param str msg: message to print
        :param Optional[bool] show_icon: should show message icon
        :return str: colored input message
        """
        return Echoes.return_message(msg=msg, icon=ICON_INFO, color=COLOR_INPUT, show_icon=show_icon)
