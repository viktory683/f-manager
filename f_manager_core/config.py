import configparser
from functools import cached_property
import json
import os
from pathlib import Path
import platform
import shutil
from typing import Optional

from f_manager_core.exceptions import GameNotFoundError, UnknownSystem
from f_manager_core.helpers import expand_path


class Config:
    class __Factorio:
        def __init__(self, data: dict) -> None:
            self.__data = data

        @cached_property
        def username(self) -> Optional[str]:
            if username := self.__data.get("username"):
                return str(username)

            with self.dir.joinpath("player-data.json").open() as f:
                player_data = json.load(f)

            if username := player_data.get("service-username"):
                return str(username)

        @cached_property
        def password(self) -> Optional[str]:
            if password := self.__data.get("password"):
                return str(password)

        @cached_property
        def token(self) -> Optional[str]:
            if token := self.__data.get("token"):
                return str(token)

            with self.dir.joinpath("player-data.json").open() as f:
                player_data = json.load(f)

            if token := player_data.get("service-token"):
                return str(token)

        @cached_property
        def dir(self) -> Path:
            path = expand_path(self.__data.get("dir"))
            try:
                exe_file = list(list(path.joinpath("bin").iterdir())[0].iterdir())[0]
                executable = shutil.which(exe_file)
                if not executable:
                    raise GameNotFoundError(
                        f"Could not find game executable file {exe_file}"
                    )
            except FileNotFoundError as e:
                raise GameNotFoundError("Could not find game executable file") from e
            return path

        @cached_property
        def mods_dir(self) -> Path:
            if path := self.__data.get("mods_dir"):
                return expand_path(path)

            return self.dir.joinpath("mods")

        @cached_property
        def data_dir(self) -> Path:
            return self.dir.joinpath("data")

        def as_dict(self) -> dict:
            exclude_keys = ["_Factorio__data"]
            return {
                key: value
                for key, value in self.__dict__.items()
                if key not in exclude_keys
            }

    class __Data:
        def __init__(self, data: dict) -> None:
            self.__data = data

        @cached_property
        def storage(self) -> Path:
            path = expand_path(self.__data.get("storage"))
            os.makedirs(path, exist_ok=True)
            return path

        def as_dict(self) -> dict:
            exclude_keys = ["_Data__data"]
            return {
                key: value
                for key, value in self.__dict__.items()
                if key not in exclude_keys
            }

    class __Logging:
        def __init__(self, data: dict) -> None:
            self.__data = data

        @cached_property
        def level(self) -> str:
            return str(self.__data.get("level"))

        @cached_property
        def path(self) -> Path:
            return expand_path(self.__data.get("path"))

        def as_dict(self) -> dict:
            exclude_keys = ["_Logging__data"]
            return {
                key: value
                for key, value in self.__dict__.items()
                if key not in exclude_keys
            }

    def __init__(self) -> None:
        match platform.system():
            case "Linux":
                self.__system = "linux"
                self.__config_dir = expand_path(Path("~/.config")).joinpath("f_manager")
            case "Darwin":
                self.__system = "mac"
                # TODO
                # self.__config_dir = Path("~/.config")
            case "Windows":
                self.__system = "win"
                # TODO
                # self.__config_dir = Path("~/.config")
            case _:
                raise UnknownSystem

        self.__sample_file = (
            Path(__file__)
            .parent.joinpath("configs")
            .joinpath(f"config_{self.__system}.ini")
        )
        if not self.__sample_file.exists():
            raise FileNotFoundError(
                f"""Can't find sample config file ({self.__sample_file}).
Try reinstall the package or find config file manually in the project page"""
            )

        self.__file = self.__config_dir.joinpath("core.ini")
        if not self.__file.exists():
            os.makedirs(self.__config_dir, exist_ok=True)
            shutil.copy(self.__sample_file, self.__file)
        # self.__file = self.__sample_file

        self.__parser = configparser.ConfigParser()
        self.__parser.read(self.__file)

    @cached_property
    def logging(self) -> __Logging:
        return self.__Logging(dict(self.__parser.items("logging")))

    @cached_property
    def data(self) -> __Data:
        return self.__Data(dict(self.__parser.items("data")))

    @cached_property
    def factorio(self) -> __Factorio:
        return self.__Factorio(dict(self.__parser.items("factorio")))

    def update(self):
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
