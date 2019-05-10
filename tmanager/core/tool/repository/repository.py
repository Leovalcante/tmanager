import git
import tmanager.utilities.dates as utl_dates
import os
from tmanager.core.tool.tool import Tool


class Repository(Tool):
    """Repository class to manage tman repository"""

    def __init__(self,
                 url: str,
                 directory: str,
                 name: str = None,
                 tags: list = None,
                 add_date: float = None,
                 install_date: float = None,
                 last_update_date: float = None):
        """
        Initialize repository

        :param str url: repository url
        :param str directory: repository installation directory
        :param str name: repository name
        :param list tags: repository tags
        :param float add_date: repository add date
        :param float install_date: repository install date
        :param float last_update_date: repository last update date
        """
        # Remove trailing slashes and add .git to the end if necessary
        url = url.rstrip("/")
        if not url.endswith(".git"):
            url += ".git"

        # Set the name is if it's None
        name = name or url.split("/")[-1][:-4]

        # Set the type
        _type = "git"

        # Set the installation directory
        if not directory.endswith(name):
            directory = "{dir}{s}{name}".format(dir=directory, s=("" if directory.endswith("/") else "/"), name=name)

        super().__init__(
            url,
            directory,
            name=name,
            _type=_type,
            tags=tags if tags else list(),
            add_date=add_date,
            install_date=install_date,
            last_update_date=last_update_date
        )

    def __str__(self, verbose: bool = False) -> str:
        """
        Return repository as string

        :param bool verbose: show all fields
        :return: repository as str
        """
        tool_desc = "\n"
        tool_desc += "name: {}\n".format(self.get_name())
        if verbose:
            tool_desc += "url: {}\n".format(self.get_url())

        tool_desc += "tags: {}\n".format(self.get_tags() if self.get_tags() else "[]")
        tool_desc += "type: {}\n".format(self.get_type())
        tool_desc += "directory: {}\n".format(self.get_directory())

        if verbose:
            tool_desc += "add date: {}\n".format("" if self.get_add_date() is None else utl_dates
                                                 .time_to_ctime(self.get_add_date()))
            tool_desc += "installation date: {}\n" \
                .format("not installed" if self.get_install_date() is None else utl_dates
                        .time_to_ctime(self.get_install_date()))

        tool_desc += "last update: {}" \
            .format("not installed" if self.get_last_update_date() is None else utl_dates
                    .time_to_ctime(self.get_last_update_date()))

        return tool_desc

    def clone(self) -> int:
        """
        Clone repository into path

        :return: int error code
        """
        return self._perform("clone")

    def update(self) -> int:
        """
        Update repository

        :return: int error code
        """
        return self._perform("pull")

    def _perform(self, func: str) -> int:
        """
        - GitPython errors: https://gitpython.readthedocs.io/en/stable/reference.html#module-git.exc
        Clone or update

        It returns:
            0 on success
            1 if the repo is already up to date (pull)
            2 if the destination directory already exists when cloning (clone)
            .. TODO ..

        :param str func: function to perform
        :return: int status code
        """
        try:
            if func == "clone":
                if os.path.isdir(self.get_directory()):             # check if the repo's directory already exists
                    return 2
                git.Repo.clone_from(self.get_url(),
                                    self.get_directory())  # if it doesn't exist, then attempt to clone it

            elif func == "pull":
                repo = git.cmd.Git(self.get_directory())
                r = repo.pull()
                if r.startswith("Already up"):
                    return 1

        except git.exc.CheckoutError:
            return 1
        except git.exc.CommandError:
            return 2
        except git.exc.GitCommandError:
            return 3
        except git.exc.GitCommandNotFound:
            return 4
        except git.exc.HookExecutionError:
            return 5
        except git.exc.InvalidGitRepositoryError:
            return 6
        except git.exc.NoSuchPathError:
            return 7
        except git.exc.RepositoryDirtyError:
            return 8
        except git.exc.UnmergedEntriesError:
            return 9
        except git.exc.WorkTreeRepositoryUnsupported:
            return 10
        except git.exc.GitError:
            return 11

        # everything went fine, modify the last_update_date
        self.last_update_date = utl_dates.now()
        return 0
