import click
import datetime

_ICON_ALERT = '[!] '
_ICON_INFO = '[*] '
_ICON_EMPTY = ''

LOG_INFO = "INFO"
LOG_WARN = "WARN"
LOG_ERR = "ERROR"


class Prints:

    @staticmethod
    def log_to_file(log_fname: str, cmd_name: str, log_lvl: str, msg: str):
        """
        Log the message 'msg' to the file log_fname.
        The log strings have the format specified below.

            yyyy/mm/gg hh:mm:ss | cmd_name | log_lvl | msg

        :param log_fname: log filename
        :param cmd_name: command name
        :param log_lvl: log level
        :param msg: the string to log
        :return:
        """
        now = datetime.datetime.now()
        date_time = "{}-{}-{} {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)

        # compute the logstring  date-cmdname-loglevel-msg
        log_str = "{} | {} | {} | {}\n".format(date_time, cmd_name, log_lvl, msg.replace("\n", "--"))

        # write the string to file
        with open(log_fname, 'a') as f:
            f.write(log_str)

        pass

    @staticmethod
    def error(msg: str, log_fname: str = "", cmd_name: str = "", icon: bool = True) -> None:
        """
        Print error messages.

        :param str msg: message to print
        :param str log_fname: log filename
        :param str cmd_name: command name
        :param bool icon: should show message icon
        :return: None
        """
        if log_fname:
            Prints.log_to_file(log_fname, cmd_name, LOG_ERR, msg)
        else:
            print_icon = _ICON_ALERT if icon else _ICON_EMPTY
            click.echo(click.style("{}{}".format(print_icon, msg), fg="red", bold=True))

    @staticmethod
    def warning(msg: str, log_fname: str = "", cmd_name: str = "", icon: bool = True) -> None:
        """
        Print warning messages.

        :param str msg: message to print
        :param str log_fname: log filename
        :param str cmd_name: command name
        :param bool icon: should show message icon
        :return: None
        """
        if log_fname:
            Prints.log_to_file(log_fname, cmd_name, LOG_WARN, msg)
        else:
            print_icon = _ICON_INFO if icon else _ICON_EMPTY
            click.echo(click.style("{}{}".format(print_icon, msg), fg="yellow", bold=True))

    @staticmethod
    def success(msg: str, log_fname: str = "", cmd_name: str = "", icon: bool = True) -> None:
        """
        Print success messages.

        :param str msg: message to print
        :param str log_fname: log filename
        :param str cmd_name: command name
        :param bool icon: should show message icon
        :return: None
        """
        if log_fname:
            Prints.log_to_file(log_fname, cmd_name, LOG_INFO, msg)
        else:
            print_icon = _ICON_INFO if icon else _ICON_EMPTY
            click.echo(click.style("{}{}".format(print_icon, msg), fg="green"))

    @staticmethod
    def info(msg: str, log_fname: str = "", cmd_name: str = "", icon: bool = True) -> None:
        """
        Print info messages.

        :param str msg: message to print
        :param str log_fname: log filename
        :param str cmd_name: command name
        :param bool icon: should show message icon
        :return: None
        """
        if log_fname:
            Prints.log_to_file(log_fname, cmd_name, LOG_INFO, msg)
        else:
            print_icon = _ICON_INFO if icon else _ICON_EMPTY
            click.echo(click.style("{}{}".format(print_icon, msg), fg="white"))

    @staticmethod
    def input(msg: str, icon: bool = True) -> None:
        """
        Print input messages.

        :param str msg: message to print
        :param bool icon: should show message icon
        :return: None
        """
        print_icon = _ICON_INFO if icon else _ICON_EMPTY
        click.echo(click.style("{}{}".format(print_icon, msg), fg="blue"))

    @staticmethod
    def verbose(msg: str, verbose: bool, log_fname: str = "", cmd_name: str = "", icon: bool = True) -> None:
        """
        Print verbose messages.

        :param str msg: message to print
        :param bool verbose: should print the message?
        :param str log_fname: log filename
        :param str cmd_name: command name
        :param bool icon: should show message icon
        :return: None
        """
        if verbose:
            if log_fname:
                Prints.log_to_file(log_fname, cmd_name, LOG_INFO, msg)
            else:
                print_icon = _ICON_INFO if icon else _ICON_EMPTY
                click.echo(click.style("{}{}".format(print_icon, msg), fg="magenta"))


class Echoes:
    @staticmethod
    def error(msg: str, icon: bool = True) -> str:
        """
        Print error messages.

        :param str msg: message to print
        :param bool icon: should show message icon
        :return str: colored error message
        """
        print_icon = _ICON_ALERT if icon else _ICON_EMPTY
        return click.style("{}{}".format(print_icon, msg), fg="red", bold=True)

    @staticmethod
    def info(msg: str, icon: bool = True) -> str:
        """
        Print info messages.

        :param str msg: message to print
        :param bool icon: should show message icon
        :return str: colored info message
        """
        print_icon = _ICON_INFO if icon else _ICON_EMPTY
        return click.style("{}{}".format(print_icon, msg), fg="white")

    @staticmethod
    def input(msg: str, icon: bool = True) -> str:
        """
        Print input messages.

        :param str msg: message to print
        :param bool icon: should show message icon
        :return str: colored input message
        """
        print_icon = _ICON_INFO if icon else _ICON_EMPTY
        return click.style("{}{}".format(print_icon, msg), fg="blue")

    @staticmethod
    def success(msg: str, icon: bool = True) -> str:
        """
        Print success messages.

        :param str msg: message to print
        :param bool icon: should show message icon
        :return str: colored success message
        """
        print_icon = _ICON_INFO if icon else _ICON_EMPTY
        return click.style("{}{}".format(print_icon, msg), fg="green")

    @staticmethod
    def verbose(msg: str, verbose: bool, icon: bool = True) -> str:
        """
        Print verbose messages.

        :param str msg: message to print
        :param bool verbose: should print the message?
        :param bool icon: should show message icon
        :return str: colored verbose message
        """
        if verbose:
            print_icon = _ICON_INFO if icon else _ICON_EMPTY
            return click.style("{}{}".format(print_icon, msg), fg="magenta")

    @staticmethod
    def warning(msg: str, icon: bool = True) -> str:
        """
        Print warning messages.

        :param str msg: message to print
        :param bool icon: should show message icon
        :return str: colored warning message
        """
        print_icon = _ICON_INFO if icon else _ICON_EMPTY
        return click.style("{}{}".format(print_icon, msg), fg="yellow", bold=True)
