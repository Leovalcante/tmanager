import click
import os
import sys
import shutil
import tmanager.core.messages.messages as msg
import tmanager.utilities.commands as utl_cmds
import tmanager.utilities.file_system as utl_fs
from tmanager.core.config.config import Config
from crontab import CronTab, CronItem
from srblib import abs_path

_available_automatic_install_true_arguments = ["true", "on", "yes"]
_available_automatic_install_false_arguments = ["false", "off", "no"]
_available_automatic_install_arguments = _available_automatic_install_true_arguments + \
                                         _available_automatic_install_false_arguments
_available_cron_job_arguments = ["create", "update", "delete", "enable", "disable", "status"]
_which_tmanager = shutil.which("tman")

CMD_NAME = "config"


@click.command()
@click.option("-d", "--default-dir", help="Change default installation directory.", metavar="<pathname>")
@click.option("-i", "--auto-install", help="Set automatic install on or off.", metavar="<on|off>")
@click.option("-j", "--cron-job", help="Create, update, enable, disable, delete or check status of Tman cron job.",
              metavar="<create|update|delete|enable|disable|status>")
@click.option("-l", "--log", help="Log to file instead of printing to stdout.", metavar="<filename>")
@click.pass_context
def config(ctx: click.core.Context, default_dir: str, auto_install: str, cron_job: str, log: str) -> None:
    """
    Manage Tman configurations.
    \f

    :param click.core.Context ctx: click context
    :param str default_dir: new default installation directory
    :param str auto_install: new auto install option
    :param str cron_job: cron job
    :param str log: log filename
    :return: None
    """
    # if a filename for logs is provided, then make sure it exists and it's writable.
    log_fname = ""
    if log:
        log_fname = utl_cmds.validate_log_filename(log, CMD_NAME)
        if not log_fname:
            sys.exit(1)

    # Get configurations and verbose
    cfg = utl_cmds.get_configs_from_context(ctx)
    vrb = utl_cmds.get_verbose_from_context(ctx)

    # Check if user is root and ask confirmation to continue, if so
    msg.Prints.verbose("Check user role", vrb)

    if os.getuid() == 0:
        msg.Prints.warning(
            "You are root. It's preferable to manage your configuration using another non-privileged account.")
        if click.confirm(msg.Echoes.input("Do you want to continue anyway?"), default=False):
            msg.Prints.warning("You have been warned!")
        else:
            sys.exit(1)

    # Check that just one option has been selected...
    msg.Prints.verbose("Check that only one option has been selected", vrb)

    # If no option is specified, then print current config. settings
    if not ((bool(default_dir) != bool(auto_install)) != bool(cron_job)):
        print("auto-install: {}".format(cfg.get_automatic_install()))
        print("default-dir : {}".format(cfg.get_default_installation_directory()))
        sys.exit(0)

    # DEFAULT INSTALLATION DIRECTORY
    if default_dir:
        _set_new_default_dir(default_dir, cfg, vrb)

    # AUTOMATIC/MANUAL INSTALL
    elif auto_install:
        _set_new_auto_install(auto_install, cfg, vrb)

    # CRON JOB CREATE
    elif cron_job:
        msg.Prints.verbose("Cron job configuration selected", vrb)
        msg.Prints.verbose("Checking argument {}".format(cron_job), vrb)

        if _check_cron_argument(cron_job):
            # Create cron
            cron = CronTab(user=True)

            # Create/Update cron job
            if cron_job == "create" or cron_job == "update":
                _cron_job_create_update(cfg, cron_job, cron, vrb)

            # Delete cron job
            elif cron_job == "delete":
                _cron_job_delete(cron, vrb)

            elif cron_job == "status":
                _cron_job_status(cron, vrb)

            elif cron_job == "enable" or cron_job == "disable":
                _cron_job_enable_disable(cron_job, cron, vrb)

        else:
            msg.Prints.error("You have to choose one among {} arguments".format(str(_available_cron_job_arguments)))
            sys.exit(1)

    sys.exit(0)


def _check_automatic_install_argument(argument: str) -> bool:
    """
    Check if --automatic-install argument is fine.

    :param str argument: --automatic-install argument
    :return bool: True if the argument is valid, False otherwise
    """
    return argument in _available_automatic_install_arguments


def _check_cron_argument(argument: str) -> bool:
    """
    Check if --cron-job argument is fine.

    :param str argument: --cron-job argument
    :return bool: True id the argument is valid, False otherwise
    """
    return argument in _available_cron_job_arguments


def _cron_job_check(value: str, min_value: int, max_value: int) -> bool:
    """
    Check if a given value is ok for cron job standards.

    :param str value: value to check
    :param int min_value: min range value
    :param int max_value: max range value
    :return bool: True if value is OK, False otherwise
    """
    # * value is always ok
    if value == "*":
        return True

    # value may be composed of several arguments separated by a ","
    value = value.split(",")
    for v in value:
        try:
            v = int(v)
            if not min_value <= v <= max_value:
                return False
        except ValueError:
            return False
    return True


def _cron_job_create_update(cfg: Config, cron_job: str, cron: CronTab, vrb: bool):
    """
    Create or update tman cron job

    :param Config cfg: tman configuration file
    :param str cron_job: action: create | update
    :param CronTab cron: users cron
    :param bool vrb: verbose output
    :return: None
    """
    msg.Prints.verbose("Cron job {} selected".format(cron_job), vrb)
    msg.Prints.verbose("Check if a tman cron job does already exist", vrb)

    cron_list = _get_cron_list(cron)

    update_cron = None
    if cron_list:
        job = _get_job_from_cron_list(cron_list)

        if cron_job == "create":
            msg.Prints.warning("A tman job does already exist")

        update_cron = click.confirm(msg.Echoes.input("Do you want to update existing job: {}".format(job)),
                                    default=False)

        if update_cron:
            msg.Prints.info("You are going to be prompted by Tman Job Wizard in order to update your job",)
            cron.remove(job)
        else:
            msg.Prints.warning("@@@ Update aborted by {}".format(utl_cmds.get_user_login()))
            raise click.Abort()

    elif not cron_list and cron_job == "update":
        msg.Prints.warning("No cron job to update found.")
        create_cron_job = click.confirm(msg.Echoes.input("Do you want to create a new cron job"), default=True)

        if not create_cron_job:
            msg.Prints.warning("@@@ Creation aborted by {}".format(utl_cmds.get_user_login()))
            raise click.Abort()

    # Start the cron job creation wizard if not update
    if not update_cron:
        _cron_job_wizard()

    msg.Prints.verbose("Getting cron job data", vrb)

    # Get cron job data:
    #       - mnt = minute
    #       - hrs = hour
    #       - dom = day of month
    #       - mth = month
    #       - dow = day of week
    mnt, hrs, dom, mth, dow, log_fname = _get_cron_job_data(cfg)

    # cron job comment
    cmt = "Tman cron job"
    cmd = "{} update --all -y -l {}".format(_which_tmanager, log_fname)

    msg.Prints.verbose("Creating cron job", vrb)

    # Create job
    job = cron.new(command=cmd, comment=cmt)

    msg.Prints.verbose("Cron job created", vrb)
    msg.Prints.verbose("Scheduling cron job according to user input", vrb)

    # Set cron job schedule
    job_schedule = "{} {} {} {} {}".format(mnt, hrs, dom, mth, dow)
    job.setall(job_schedule)

    msg.Prints.verbose("Cron job scheduled {}".format(job), vrb)

    # Check if cron job is valid
    msg.Prints.verbose("Checking job validity", vrb)

    try:
        assert job.is_valid
    except AssertionError:
        raise click.ClickException(msg.Echoes.error("@@@ The cron job `{}` is invalid.".format(job)))

    # Ask user confirmation to create the cron job
    msg.Prints.info("You are about to write this job: '{}'".format(job))
    if click.confirm(msg.Echoes.input("@@@ Do you want to save the cron job?"), default=False):
        cron.write()
        msg.Prints.success("@@@ Cron job saved!")
        # msg.Prints.success("@@@ The Wizard has finally accomplished his quest successfully, now he will go away! @@@")
    else:
        msg.Prints.warning("@@@ Creation aborted by {}".format(utl_cmds.get_user_login()))
        raise click.Abort()


def _cron_job_delete(cron: CronTab, vrb: bool) -> None:
    """
    Delete tman cron job.

    :param CronTab cron: users cron
    :param bool vrb: verbose output
    :return: None
    """
    msg.Prints.verbose("Cron job delete selected", vrb)
    msg.Prints.verbose("Looking for cron job", vrb)

    # Find cron job
    cron_list = _get_cron_list(cron)
    job = _get_job_from_cron_list(cron_list)

    msg.Prints.verbose("Cron job found: {}".format(job), vrb)
    msg.Prints.verbose("Attempting to remove it", vrb)

    # Delete job
    cron.remove(job)
    msg.Prints.success("Cron job deleted")

    cron.write()


def _cron_job_enable_disable(cron_job: str, cron: CronTab, vrb: bool) -> None:
    """
    Enable or disable tman cron job.

    :param str cron_job: action: enable | disable
    :param CronTab cron: users cron
    :param bool vrb: verbose output
    :return: None
    """
    msg.Prints.verbose("Cron job {} selected".format(cron_job), vrb)
    msg.Prints.verbose("Looking for cron job", vrb)

    # Find cron job
    cron_list = _get_cron_list(cron)
    job = _get_job_from_cron_list(cron_list)

    msg.Prints.verbose("Cron job found: {}".format(job), vrb)

    # Enable cron job
    _enable_cron_job(cron, job, True if cron_job == "enable" else False)


def _cron_job_status(cron: CronTab, vrb: bool) -> None:
    """
    Check tman cron job status.

    :param CronTab cron: users cron
    :param bool vrb: verbose output
    :return: None
    """
    msg.Prints.verbose("Cron job status selected", vrb)
    msg.Prints.verbose("Looking for cron job", vrb)

    # Find cron job
    cron_list = _get_cron_list(cron)
    job = _get_job_from_cron_list(cron_list)

    # Check cron status
    msg.Prints.success("Cron job found: {}".format(job))
    msg.Prints.success("Cron job status: {}".format("enabled" if job.is_enabled() else "disabled"))
    msg.Prints.success("Cron job validity: {}".format(job.is_valid()))


def _cron_job_wizard() -> None:
    """
    Print the description of cron job wizard to create cron job.

    :return: None
    """
    msg.Prints.success("@@@ Welcome to Tman Job Wizard @@@")
    msg.Prints.info(
        "@@@ We assume that you know what a cron job is, if not please read first https://en.wikipedia.org/wiki/Cron")
    msg.Prints.info(
        "@@@ To support every system, Tman does not support nonstandard predefined scheduling definitions")
    msg.Prints.info("@@@ The only allowed special character is \",\"")
    msg.Prints.info("@@@ So please use standard cron tab notation:")
    msg.Prints.info("@@@ ┌───────────── minute (0 - 59)")
    msg.Prints.info("@@@ │ ┌───────────── hour (0 - 23)")
    msg.Prints.info("@@@ │ │ ┌───────────── day of the month (1 - 31)")
    msg.Prints.info("@@@ │ │ │ ┌───────────── month (1 - 12)")
    msg.Prints.info("@@@ │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday)")
    msg.Prints.info("@@@ * * * * * command to execute\n")
    msg.Prints.info("@@@ Now you will be asked several question, in order to create tmanager automatic update job")
    msg.Prints.info("@@@ Leave it blank to * the info")


def _enable_cron_job(cron: CronTab, job: CronItem, enable: bool = True) -> None:
    """
    Enable/Disable a cron job.

    :param CronTab cron: cron
    :param CronItem job: cron job
    :param bool enable: False if user want to disable a cron job, True otherwise
    """
    job.enable(enable)
    msg.Prints.success("Cron job has been {}".format("enabled" if job.is_enabled() else "disabled"))
    cron.write()


def _get_cron_job_data(cfg: Config) -> list:
    """
    Get all cron job required data:
        - minute
        - hour
        - day of the month
        - month
        - day of the week
        - log file where to save cron spool
    And validate it.

    :param Config cfg: tman condifguration
    :return list: validated list of cron job data
    """
    # default log file
    default_logfile = "{}{}".format(utl_fs.trailing_slash(cfg.config_dir), "tman-cron.log")

    # Get cron job data
    mnt = click.prompt(msg.Echoes.input("@@@ Insert minute (0 - 59)"), default="*")
    hrs = click.prompt(msg.Echoes.input("@@@ Insert hour (0 - 23)"), default="*")
    dom = click.prompt(msg.Echoes.input("@@@ Insert day of the month (1 - 31)"), default="*")
    mth = click.prompt(msg.Echoes.input("@@@ Insert month (1 - 12)"), default="*")
    dow = click.prompt(msg.Echoes.input("@@@ Insert day of the week (0 - 6) (Sunday to Saturday)"), default="*")
    log = click.prompt(msg.Echoes.input("@@@ Enter a file pathname for logging stuffs?"), default=default_logfile)

    # Check data consistency
    if not _cron_job_check(mnt, 0, 59):
        _raise_cron_input_data_exception("minute", "(0 - 59)")

    if not _cron_job_check(hrs, 0, 23):
        _raise_cron_input_data_exception("hour", "(0 - 23)")

    if not _cron_job_check(dom, 1, 31):
        _raise_cron_input_data_exception("day of month", "(1 - 31)")

    if not _cron_job_check(mth, 1, 12):
        _raise_cron_input_data_exception("month", "(1 - 12)")

    if not _cron_job_check(dow, 0, 6):
        _raise_cron_input_data_exception("day of week", "(0 - 6)")

    # if a filename for logging has been provided by the user, do the required checks and prompt the user when needed
    if log != default_logfile:
        log = utl_cmds.validate_log_filename(log, CMD_NAME)
        if not log:
            sys.exit(1)

    # Remove spaces, they will cause error in cron job writing
    mnt = mnt.replace(" ", "")
    hrs = hrs.replace(" ", "")
    dom = dom.replace(" ", "")
    mth = mth.replace(" ", "")
    dow = dow.replace(" ", "")

    return [mnt, hrs, dom, mth, dow, log]


def _get_cron_list(cron: CronTab) -> list:
    """
    Find Tman cron job.

    :param CronTab cron: Users cron
    :return list: tman cron job list
    """
    return list(cron.find_command("tman"))


def _get_job_from_cron_list(cron_list: list) -> CronItem:
    """
    Return CronItem from cron list, if not found raise an exception .

    :param list cron_list: cron job list
    :return CronItem: Job if found, otherwise raise an exception
    """
    try:
        job = cron_list[0]
    except IndexError:
        msg.Prints.error("Cron job not found")
        raise click.Abort()

    return job


def _is_automatic_install_true(argument: str) -> bool:
    """
    Check if --automatic-install argument is True.

    :param str argument: --automatic-install argument
    :return bool: True if the argument is True, False otherwise
    """
    return argument in _available_automatic_install_true_arguments


def _is_automatic_install_false(argument: str) -> bool:
    """
    Check if --automatic-install argument is False.

    :param str argument: --automatic-install argument
    :return bool: True if the argument is False, False otherwise
    """
    return argument in _available_automatic_install_false_arguments


def _raise_automatic_install_exception() -> None:
    """
    Raise click BadOptionUsage for --automatic-install configurations.

    :return: None
    """
    raise click.BadOptionUsage("Automatic Install Option Error",
                               msg.Echoes.error("Please select one among the available options: {}"
                                                .format(str(_available_automatic_install_arguments))))


def _raise_cron_input_data_exception(param: str, param_hint: str) -> None:
    """
    Raise click BadParameter for cron job creation data error.

    :param str param: wrong parameters
    :param str param_hint: parameters hint
    :return: None
    """
    param = param.capitalize()
    param_hint = "{} value MUST BE in {} range".format(param, param_hint)
    raise click.BadParameter(
        msg.Echoes.error("@@@ {} parameter does not respect the rules. That's not cool man...").format(param),
        param=param, param_hint=param_hint)


def _set_new_auto_install(auto_install: str, cfg: Config, vrb: bool) -> None:
    """
    Set new config automatic install.

    :param str auto_install: automatic install value
    :param Config cfg: configuration object
    :param bool vrb: verbose output
    :return: None
    """
    msg.Prints.verbose("Change automatic install selected", vrb)

    new_automatic_install = None

    msg.Prints.verbose("Check if given input is valid: {}".format(auto_install), vrb)

    if _check_automatic_install_argument(auto_install):
        if _is_automatic_install_true(auto_install):
            new_automatic_install = True

        elif _is_automatic_install_false(auto_install):
            new_automatic_install = False

        else:
            _raise_automatic_install_exception()

    else:
        _raise_automatic_install_exception()

    msg.Prints.verbose("Automatic install has been set to {}".format(new_automatic_install), vrb)

    cfg.set_automatic_install(new_automatic_install)
    msg.Prints.success("Automatic install has been {}".format("enabled" if new_automatic_install else "disabled"))
    cfg.save()


def _set_new_default_dir(default_dir: str, cfg: Config, vrb: bool) -> None:
    """
    Set new default installation directory.

    :param str default_dir: New default installation directory
    :param Config cfg: configuration object
    :param bool vrb: verbose output
    :return: None
    """
    # Get the absolute path of new default installation directory
    default_dir = abs_path(default_dir)

    msg.Prints.verbose("Change default installation directory selected", vrb)

    # Check if directory exists, if not create it first
    msg.Prints.verbose("Check if new directory {} exists".format(default_dir), vrb)
    if not os.path.isdir(default_dir):
        msg.Prints.verbose("New directory {} does not exist".format(default_dir), vrb)

        os.makedirs(default_dir)
        msg.Prints.verbose("{} created".format(default_dir), vrb)

    msg.Prints.verbose("Setting new default installation directory", vrb)

    cfg.set_default_installation_directory(default_dir)
    msg.Prints.success("Default installation directory directory changed in {}".format(default_dir))
    cfg.save()
