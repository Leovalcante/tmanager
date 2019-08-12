import click
import os
import fnmatch
import sys
import time
import threading
import git
import tmanager.core.messages.messages as msg
import tmanager.utilities.file_system as utl_fs
import tmanager.utilities.commands as utl_cmds

from tmanager.core.tool.repository.repository import Repository


@click.command(options_metavar="", short_help="Scan filesystem seeking repositories.")
@click.argument("root-dir", required=False, metavar="<root-dir>")
@click.pass_context
def scan(ctx: click.core.Context, root_dir: str) -> None:
    """
    \b
    Scan filesystem seeking repositories starting from <root-dir>.
    If no <root-dir> is specified it will start scanning the system from your home directory.
    \f

    :param click.core.Context ctx: click context
    :param str root_dir: directory to start scanning by searching repositories
    :return: None
    """
    # Get configuration object and verbose
    cfg = utl_cmds.get_configs_from_context(ctx)
    vrb = utl_cmds.get_verbose_from_context(ctx)

    # Set initial variable value
    root_dir = root_dir or utl_fs.get_home_env()

    if not os.path.isdir(root_dir):
        raise click.BadArgumentUsage(msg.Echoes.error(f"{root_dir} is not a directory"))

    msg.Prints.info(f"Using {root_dir} as root dir")
    msg.Prints.info("Scanning system for git repositories. This may take a while")

    # Scan the system for git repositories
    repos_list = []
    msg.Prints.verbose("Start searching daemon", vrb)

    search = threading.Thread(name='repo_search', target=_repo_seeker, args=(root_dir, repos_list))
    search.daemon = True
    search.start()

    try:
        while search.is_alive():
            _animated_loading()
    except KeyboardInterrupt:
        msg.Prints.verbose("Searching deamon has been stopped", vrb)
        msg.Prints.verbose("Quitting...", vrb)
        raise click.Abort()

    # Delete "searching..." line
    sys.stdout.write("\r")

    msg.Prints.warning(f"{len(repos_list)} repositories found")

    # Found some repos?
    if repos_list:
        msg.Prints.verbose("Listing repositories", vrb)

        # List repositories found
        i = 0
        for repo in repos_list:
            name = repo.split("/")[-1]
            msg.Prints.info(f"{i + 1}. {name}, {repo}")
            i += 1

        # Ask the user to add all repositories found
        add_it_all = click.confirm(msg.Echoes.input("Do you want to add all of them?"), default=False)

        # OK, add all repositories found to tman
        if add_it_all:
            msg.Prints.info("All repositories found will be added in tman")
            msg.Prints.verbose("All repositories found are going to be added", vrb)
            msg.Prints.verbose("Generating repositories indexes", vrb)

            chosen_indexes = [*range(len(repos_list))]

        # KO, ask to user which repository should be added
        else:
            msg.Prints.verbose("Do not add all repositories", vrb)

            chosen_indexes = click.prompt(msg.Echoes.input("Enter the numbers of the repo you want to add, separated "
                                                           "by a comma"), default="q")

            if chosen_indexes != "q":
                msg.Prints.verbose("There are some repositories to add", vrb)
                msg.Prints.verbose("Validate all user input indexes", vrb)

                # Sanitize input
                chosen_indexes = utl_cmds.sanitize_indexes(repos_list, chosen_indexes)

                msg.Prints.verbose("Indexes sanitized: {chosen_indexes}", vrb)

                # If there are any indexes after index sanitize
                if chosen_indexes:
                    msg.Prints.verbose("Listing all repositories user wants to add", vrb)

                    # Print the repositories that will be added

                    if vrb:
                        msg.Prints.warning("The following repositories will be added in tman:")
                        for i in chosen_indexes:
                            path = repos_list[i]
                            name = path.split("/")[-1]
                            msg.Prints.info(f"{name}, {path}")

                else:
                    # There isn't any valid index, print error message and quit
                    msg.Prints.error("None of the supplied indexes is valid")
                    raise click.Abort()

            # User choose to not add any repository
            else:
                msg.Prints.info("No repository will be add")
                return

        msg.Prints.verbose("Start to add desired repositories", vrb)

        # Add selected repositories to tman
        for i in chosen_indexes:
            repo_dir = repos_list[i]
            repo_name = repo_dir.split("/")[-1]
            git_repo = git.Repo(repo_dir)
            try:
                repo_url = git_repo.remote("origin").url
            except ValueError:
                msg.Prints.warning(f"Skipping {repo_name}, no origin found")
                continue

            add_time = time.time()
            repository = Repository(repo_url, repo_dir, name=repo_name, add_date=add_time,
                                    install_date=add_time, last_update_date=add_time)

            msg.Prints.verbose(f"{repository.__str__(True)} is going to be added", vrb)

            if not any(t.get_name() == repository.get_name() for t in cfg.get_tools()):
                cfg.add_tool(repository)
                msg.Prints.success(f"{repository.get_name()} successfully added")

            else:
                msg.Prints.warning(f"{repository.get_name()} has already been added. Skipping...")

        msg.Prints.verbose("All repositories have been added", vrb)
        msg.Prints.verbose("Proceed to save new configurations", vrb)

        cfg.save()

        msg.Prints.verbose("Configurations saved", vrb)
        msg.Prints.verbose("tman scan execution completed", vrb)
    sys.exit(0)


def _repo_seeker(root_dir: str, repo_list: list) -> None:
    """
    Search repositories from root_dir.
    NOTE: THIS FUNCTION IS CALLED WITHIN A THREAD

    :param str root_dir: root directory where to start the scan
    :param list repo_list: repository list to populate
    :return: None
    """
    pattern = ".git"

    for root, dirs, file in os.walk(root_dir):
        for d in dirs:
            if fnmatch.fnmatch(d, pattern):
                repo_list.append(root)


def _animated_loading() -> None:
    """
    Print a loading statement while searching for repositories.

    :return: None
    """
    chars = "/—\\|"
    for char in chars:
        sys.stdout.write("\r" + char + " searching...")
        time.sleep(.1)
        sys.stdout.flush()
