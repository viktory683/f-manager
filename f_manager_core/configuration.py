import configparser
from functools import cached_property
import json
from pathlib import Path
import platform
import shutil
from typing import Optional

from f_manager_core.exceptions import GameNotFoundError, UnknownSystem
from f_manager_core.helpers import expand_path


class ConfigSection:
    """Base class for configuration sections."""

    def __init__(self, data: dict) -> None:
        self._data = data

    def as_dict(self) -> dict:
        """Return the section data as a dictionary."""
        exclude_keys = ["_data"]
        return {
            key: value
            for key, value in self.__dict__.items()
            if key not in exclude_keys
        }


class FactorioConfigSection(ConfigSection):
    """Class for the Factorio configuration section."""

    @cached_property
    def username(self) -> Optional[str]:
        """Return the Factorio username."""
        if username := self._data.get("username"):
            return str(username)

        with self.dir.joinpath("player-data.json").open() as f:
            player_data = json.load(f)

        if username := player_data.get("service-username"):
            return str(username)

    @cached_property
    def password(self) -> Optional[str]:
        """Return the Factorio password."""
        if password := self._data.get("password"):
            return str(password)

    @cached_property
    def token(self) -> Optional[str]:
        """Return the Factorio token."""
        if token := self._data.get("token"):
            return str(token)

        with self.dir.joinpath("player-data.json").open() as f:
            player_data = json.load(f)

        if token := player_data.get("service-token"):
            return str(token)

    @cached_property
    def dir(self) -> Path:
        """Return the Factorio directory."""
        path = expand_path(self._data.get("dir"))
        try:
            exe_file = list(list(path.joinpath("bin").iterdir())[0].iterdir())[0]
            executable = shutil.which(exe_file)
            if not executable:
                raise GameNotFoundError(f"Could not find game executable file {exe_file}")
        except FileNotFoundError as e:
            raise GameNotFoundError("Could not find game executable file") from e
        return path

    @cached_property
    def mods_dir(self) -> Path:
        """Return the Factorio mods directory."""
        if path := self._data.get("mods_dir"):
            return expand_path(path)

        return self.dir.joinpath("mods")

    @cached_property
    def data_dir(self) -> Path:
        """Return the Factorio data directory."""
        return self.dir.joinpath("data")


class DataConfigSection(ConfigSection):
    """Class for the data configuration section."""

    @cached_property
    def storage(self) -> Path:
        """Return the data storage directory."""
        path = expand_path(self._data.get("storage"))
        path.mkdir(parents=True, exist_ok=True)
        return path


class LoggingConfigSection(ConfigSection):
    """Class for the logging configuration section."""

    @cached_property
    def level(self) -> str:
        """Return the logging level."""
        return str(self._data.get("level"))

    @cached_property
    def path(self) -> Path:
        """Return the logging path."""
        return expand_path(self._data.get("path"))


class Config:
    """Class for managing the configuration file."""

    def __init__(self) -> None:
        self.__system = self.get_system()
        self.__config_dir = self.get_config_dir()
        self.__sample_file = self.get_sample_file()
        self.__file = self.get_config_file()
        self.__parser = self.get_config_parser()

    def get_system(self) -> str:
        """Return the current system."""
        system = platform.system()
        systems = {
            "Linux": "linux",
            "Darwin": "mac",
            "Windows": "win",
        }

        if s := systems.get(system):
            return s

        raise UnknownSystem

    def get_config_dir(self) -> Path:
        """Return the configuration directory."""
        user_home_dirs = {
            "linux": "~/.config",
            "mac": "~/Library/Application Support",
            "win": "%APPDATA%",
        }

        config_dir = expand_path(user_home_dirs[self.__system]).joinpath("f_manager")
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def get_sample_file(self) -> Path:
        """Return the sample configuration file."""
        sample_file = (
            Path(__file__)
            .parent.joinpath("configs")
            .joinpath(f"config_{self.__system}.ini")
        )
        if not sample_file.exists():
            raise FileNotFoundError(
                f"Can't find sample config file ({sample_file}). Try reinstalling the package or finding the config file manually on the project page"  # noqa: E501
            )
        return sample_file

    def get_config_file(self) -> Path:
        """Return the configuration file."""
        config_file = self.__config_dir.joinpath("core.ini")
        if not config_file.exists():
            shutil.copy(self.__sample_file, config_file)
        return config_file

    def get_config_parser(self) -> configparser.ConfigParser:
        """Return the configuration parser."""
        parser = configparser.ConfigParser()
        parser.read(self.__file)
        return parser

    @cached_property
    def logging(self) -> LoggingConfigSection:
        """Return the logging configuration section."""
        return LoggingConfigSection(dict(self.__parser.items("logging")))

    @cached_property
    def data(self) -> DataConfigSection:
        """Return the data configuration section."""
        return DataConfigSection(dict(self.__parser.items("data")))

    @cached_property
    def factorio(self) -> FactorioConfigSection:
        """Return the Factorio configuration section."""
        return FactorioConfigSection(dict(self.__parser.items("factorio")))

    def update(self):
        """Update the configuration file."""
        factorio_dict = self.factorio.as_dict()
        for key, value in factorio_dict.items():
            if value:
                self.__parser["factorio"][key] = str(value)

        data_dict = self.data.as_dict()
        for key, value in data_dict.items():
            if value:
                self.__parser["data"][key] = str(value)

        logging_dict = self.logging.as_dict()
        for key, value in logging_dict.items():
            if value:
                self.__parser["logging"][key] = str(value)

        with self.__file.open("w") as f:
            self.__parser.write(f)


config = Config()
