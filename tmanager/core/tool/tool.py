from abc import ABC, abstractmethod


class Tool(ABC):
    """Repository class to manage tman repository."""
    def __init__(self,
                 url: str,
                 directory: str,
                 name: str = None,
                 _type: str = None,
                 tags: list = None,
                 add_date: float = None,
                 install_date: float = None,
                 last_update_date: float = None):
        """
        Initialize tool.

        :param str url: tool url
        :param str directory: tool installation directory
        :param str name: tool name
        :param str _type: tool type
        :param list tags: tool tags
        :param float add_date: tool add date
        :param float install_date: tool install date
        :param float last_update_date: tool last update date
        """
        self._url = url
        self._directory = directory
        self._name = name
        self._type = _type
        self._tags = tags
        self._add_date = add_date
        self._install_date = install_date
        self._last_update_date = last_update_date

    def __dict__(self) -> dict:
        """
        Return tool as dict.

        :return: tool as dict
        """
        return {
            "name": self._name,
            "url": self._url,
            "tags": self._tags,
            "type": self._type,
            "directory": self._directory,
            "add_date": self._add_date,
            "install_date": self._install_date,
            "last_update_date": self._last_update_date
        }

    def __eq__(self, other) -> bool:
        """
        Check if other tool is equal to self tool

        :param Tool other: other Tool to check
        :return bool: True if self == other, False otherwise
        """
        return self.get_name() == other.get_name()

    @abstractmethod
    def __str__(self):
        pass

    # GETTER & SETTER
    # URL
    def get_url(self) -> str:
        """
        Get tool url

        :return: tool url
        """
        return self._url

    def set_url(self, new_url: str) -> None:
        """
        Set new url for tool

        :param str new_url: new url to use as url
        :return: None
        """
        self._url = new_url

    # DIRECTORY
    def get_directory(self) -> str:
        """
        Get tool directory

        :return: tool directory
        """
        return self._directory

    def set_directory(self, new_dir: str) -> None:
        """
        Set new directory for tool

        :param str new_dir: new path to use as directory
        :return: None
        """
        if not new_dir.endswith("/"):
            new_dir += "/"

        self._directory = new_dir + self._name

    # NAME
    def get_name(self) -> str:
        """
        Get tool name

        :return: tool name
        """
        return self._name

    def set_name(self, new_name: str) -> None:
        """
        Set new name for tool

        :param str new_name: new name to use as name
        :return: None
        """
        self._name = new_name

    # TYPE
    def get_type(self) -> str:
        """
        Get tool type

        :return: tool type
        """
        return self._type

    def set_type(self, new_type: str) -> None:
        """
        Set new type for tool

        :param str new_type: new type to use as type
        :return: None
        """
        self._type = new_type

    # TAGS
    def get_tags(self) -> list:
        """
        Get tool tags

        :return: tool tags
        """
        return self._tags

    def set_tags(self, new_tags: list) -> None:
        """
        Set new tags

        :param list new_tags: new tags list to use as tags
        :return: None
        """
        self._tags = new_tags

    # ADD DATE
    def get_add_date(self) -> float:
        """
        Get tool add date

        :return: tool add date
        """
        return self._add_date

    def set_add_date(self, new_add_date: float) -> None:
        """
        Set new add date

        :param float new_add_date: new add date to use as add date
        :return: None
        """
        self._add_date = new_add_date

    # INSTALL DATE
    def get_install_date(self) -> float:
        """
        Get tool install date

        :return: tool install date
        """
        return self._install_date

    def set_install_date(self, new_install_date: float) -> None:
        """
        Set new install date

        :param float new_install_date: new install date to use as install date
        :return: None
        """
        self._install_date = new_install_date

    # LAST UPDATE DATE
    def get_last_update_date(self) -> float:
        """
        Get tool last update date

        :return: tool last update date
        """
        return self._last_update_date

    def set_last_update_date(self, new_last_update_date: float) -> None:
        """
        Set new install date

        :param float new_last_update_date: new last update date to use as last update date
        :return: None
        """
        self._last_update_date = new_last_update_date

    @abstractmethod
    def update_timestamps(self) -> None:
        """
        Update the repository installation date and its last update date.

        :return: None
        """
        pass

    @abstractmethod
    def is_installed(self) -> bool:
        """
        Check if the tool is installed or not.

        :return bool: True if the tool is installed, False otherwise
        """
        pass
