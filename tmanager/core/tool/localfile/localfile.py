from tmanager.core.tool.tool import Tool
import tmanager.utilities.dates as utl_dates
import tmanager.utilities.file_system as utl_fs


class LocalFile(Tool):
    """Repository class to manage tman repository."""
    def __init__(self,
                 pathname: str,
                 directory: str = None,
                 tags: list = None,
                 add_date: float = None,
                 install_date: float = None,
                 last_update_date: float = None):
        """
        Initialize Local File.

        :param pathname:
        :param directory:
        :param tags:
        :param add_date:
        :param install_date:
        :param last_update_date:
        """
        # No url required for local files
        url = "-"

        # Remove trailing slashes
        pathname = pathname.rstrip("/")

        # Retrieve name
        name = pathname.split("/")[-1]

        # Initialize type
        _type = "local"

        # Set the install_dir if it's None
        if directory is None:
            directory = pathname

        t = []
        super().__init__(
            url,
            directory,
            name=name,
            _type=_type,
            tags=tags if tags else t,
            add_date=add_date,
            install_date=install_date,
            last_update_date=last_update_date
        )

    def __str__(self, verbose: bool = False) -> str:
        """
        Return local file as string.

        :return: local file as str
        """
        tool_desc = "\n"
        tool_desc += f"name: {self.get_name()}\n"
        tool_desc += f"tags: {self.get_tags()}\n"
        tool_desc += f"type: {self.get_type()}\n"
        tool_desc += f"directory: {self.get_directory()}"
        if verbose:
            tool_desc += f"add date: " \
                f"{'' if self.get_add_date() is None else utl_dates.time_to_ctime(self.get_add_date())}\n"
        else:
            tool_desc += "\n"

        return tool_desc

    def update_timestamps(self):    # TODO: this is useless, check if is it possible to remove it
        """
        Update the repository installation date and its last update date.

        :return: None
        """
        pass

    def is_installed(self):
        """
        Check if the local file is on the file system or not.

        :return bool: True if the tool is present, False otherwise
        """
        if utl_fs.exists_pathname(self._directory):
            return True

        return False
