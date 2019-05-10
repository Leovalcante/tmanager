import os
import json
import click
import tmanager.core.messages.messages as msg
from tmanager.core.tool.tool import Tool
from tmanager.core.tool.repository.repository import Repository
from tmanager.core.tool.localfile.localfile import LocalFile
import tmanager.utilities.file_system as utl_fs


class Config(dict):
    """Config class to manage tman configurations"""

    def __init__(self, *args, **kwargs):
        """
        Initialize configuration.

        :param args:
        :param kwargs:
        """
        home_path = os.getenv("HOME")
        tman_config_path = "{}/.tman".format(home_path)
        tman_config_file = "{}/config.json".format(tman_config_path)

        self.config_dir = tman_config_path
        self.config_file = tman_config_file

        super(Config, self).__init__(*args, **kwargs)

    def load(self, importing: bool = None) -> int:
        """
        Load tman configurations.

        :param bool importing: flag set for import configuration option
        :return: int status code
        """
        # Just return 1 if there's no default installation directory AND it's importing configurations from a file
        if not os.path.isdir(self.config_dir) and importing is True:
            return 1

        cfg = None
        try:
            cfg = open(self.config_file, "r")
        except FileNotFoundError:
            self.first_configuration()
            cfg = open(self.config_file, "r")
        finally:
            configs = cfg.read()
            cfg.close()
            self.update(json.loads(configs))

        return 0

    def save(self) -> None:
        """
        Save tman configuration.

        :return: None
        """
        if not os.path.isdir(self.config_dir):
            os.makedirs(self.config_dir)

        with open(self.config_file, "w") as cfg:
            cfg.write(json.dumps(self))

    def is_empty(self) -> bool:
        """
        Returns True if the configuration file is empty,
        otherwise it returns False.

        :return bool: True if configurations are empty, False otherwise
        """
        return bool(self)

    def initialize_empty_tool_list(self) -> None:
        """
        Initialize the tools list

        :return: None
        """
        self["tools"] = []

    def get_tools(self, repo_only: bool = False) -> list:
        """
        Returns every Tool managed by tman.

        :param repo_only: should extract only repositories?
        :return list: tool list
        """
        tools = []

        for tool in self["tools"]:
            if tool["url"] != "-":
                res_tool = Repository(
                    tool["url"],
                    tool["directory"],
                    name=tool["name"],
                    tags=tool["tags"],
                    add_date=tool["add_date"],
                    install_date=tool["install_date"],
                    last_update_date=tool["last_update_date"])
            else:
                res_tool = LocalFile(
                    tool["directory"],
                    tags=tool["tags"],
                    add_date=tool["add_date"])

            if res_tool:
                # Skip local files if the repo_only is True
                if repo_only and res_tool.is_localfile():
                    continue

                tools.append(res_tool)

        return tools

    def already_managed(self, tool: Tool) -> bool:
        """
        Check if the input Tool is already managed by tman.

        :param Tool tool: tool to check
        :return bool: True if it is, otherwise it returns False
        """
        for t in self.get_tools():
            if tool.get_name() == t.get_name():
                return True
            # Check if it's a subdirectory of a managed tool
            elif os.path.isdir(t.get_directory()):
                if tool.get_directory().startswith(t.get_directory()):
                    return True

        return False

    def get_tool(self, tool_name: str) -> Tool or None:
        """
        Return a Tool by name.

        :param str tool_name: tool name to find
        :return Tool|None: found tool or None
        """
        for tool in self.get_tools():
            if tool.get_name() == tool_name:
                return tool

        return None

    def add_tool(self, tool: Tool) -> None:
        """
        Add tool to configuration file.

        :param Tool tool: repository to add
        :return: None
        """
        self["tools"].append(tool.__dict__())

    def update_tool(self, tool: Tool) -> None:
        """
        Update given tool.

        :param Tool tool: tool to update
        :return: None
        """
        for t in self.get_tools():
            if t.get_name() == tool.get_name():
                self.remove_tool(t)
                self.add_tool(tool)

    def remove_tool(self, tool: Tool) -> None:
        """
        Remove a repository from repositories.

        :param Tool tool: tool to remove
        :return: None
        """
        self["tools"].remove(tool.__dict__())

    def remove_all_tools(self) -> int:
        """
        Remove all repositories saved in configuration file.

        :return int: number of tools removed
        """
        length = len(self["tools"])
        self["tools"] = []
        return length

    def auto_install(self) -> None:
        """
        If auto_install is set, then attempt to
        install every repo that hasn't yet been installed.
        If auto_install is NOT set, then this method does nothing.

        :return: None
        """
        if self.get_automatic_install():
            msg.Prints.info("Installing repositories, this may take a while..", "", "")
            tot = 0
            for repo in self.get_tools(repo_only=True):
                if repo.clone() == 0:
                    tot += 1
                    # Update both the installation date and the last update date
                    repo.update_timestamps()
                    self.update_tool(repo)
                    self.save()
            msg.Prints.info("{} repo cloned".format(tot), "", "")

    def get_automatic_install(self) -> bool:
        """
        Get automatic install option.

        :return bool: True if automatic install is on, False otherwise
        """
        return self["automatic_install"]

    def set_automatic_install(self, automatic_install: bool) -> None:
        """
        Set automatic install value.

        :param bool automatic_install: True if automatic install is on, False otherwise
        :return: None
        """
        self["automatic_install"] = automatic_install

    def get_default_installation_directory(self) -> str or None:
        """
        Return the default installation directory for repository.

        :return str|None: default installation directory if exists or None
        """
        if "default_installation_directory" in self.keys():
            return utl_fs.trailing_slash(self["default_installation_directory"])

        return None

    def has_tool(self, name: str) -> bool:
        """
        Check if given name is already signed into tman tools.

        :param name: tool name to search
        :return bool: True if tool is into configuration file, False otherwise
        """
        tools = self.get_tools()
        for t in tools:
            if t.get_name() == name:
                return True

        return False

    def set_default_installation_directory(self, new_installation_directory: str) -> None:
        """
        Set a new default installation directory.

        :param str new_installation_directory:
        :return: None
        """
        self["default_installation_directory"] = new_installation_directory

    def first_configuration(self, importing=False) -> None:
        """
        Guide the user through the very first setup of tman configuration.

        :return: None
        """
        if not importing:
            msg.Prints.warning("Configuration file not found!", "", "")

        # Check if configuration directory exists, otherwise create it
        if not os.path.isdir(self.config_dir):
            os.makedirs(self.config_dir)

        # Guide the user through the very first setup
        if click.confirm(msg.Echoes.input("Would you like to use {} as your default installation directory? "
                                          .format(self.config_dir)), default=True):
            default_installation_directory = self.config_dir
        else:
            default_installation_directory = click.prompt(
                msg.Echoes.input("Please select default installation directory for your repositories"))

        automatic_install = click.confirm(msg.Echoes.input("Do you want to set automatic installation?"), default=True)

        self["default_installation_directory"] = default_installation_directory
        self["automatic_install"] = automatic_install
        self["tools"] = []

        self.save()
        msg.Prints.success("Configuration file {} has been created successfully".format(self.config_file), "", "")
