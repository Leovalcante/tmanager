import click
import time
import datetime
import tmanager.core.messages.messages as msg


def time_to_ctime(posix_time: float) -> str:
    """
    Transform seconds since epoch time into human readable time.

    :param posix_time: seconds since epoch
    :return: human readable time
    """
    return time.ctime(posix_time)


def now() -> float:
    """
    Returns the current datetime.

    :return float: time now: seconds since epoch
    """
    return time.time()


def date_to_epoch(date_time: str) -> float:
    """
    Returns the 'epoch-time' equivalent of the date taken as a parameter.

    :param str date_time: date to convert in epoch. It MUST BE in dd-mm-yyyy format
    :return float: seconds to epoch
    """
    try:
        date_time = str(datetime.datetime.strptime(date_time, '%d-%m-%Y')).split(" ")[0]
    except ValueError:
        raise click.BadParameter(msg.Echoes.error("Bad data format! It must be dd-mm-yyyy"), param="--last-update-date",
                                 param_hint="Date format MUST BE dd-mm-yyyy")

    date_time = "{}-0-0-0-0-0-0".format(date_time)
    # noinspection PyTypeChecker
    date_time = time.mktime(tuple([int(e) for e in date_time.split("-")]))
    return date_time
