from __future__ import annotations

import json
import os
import platform
import shutil
from pathlib import Path

import yaml

from f_manager.helpers import Singleton, expand_path


def join_constructor(loader, node):
    seq = loader.construct_sequence(node)
    return ''.join(seq)


# TODO: docstring
class Config(metaclass=Singleton):
    def __init__(self) -> None:  # sourcery skip: last-if-guard
        if not hasattr(self, "_config"):
            self._platform = platform.system().lower()

            default_dir = Path(__file__).parent.joinpath("config")
            default_path = default_dir.joinpath(f"default_{self._platform}.yaml")

            user_dir = None
            if self._platform in ("linux", "darwin"):
                user_dir = Path.home().joinpath(".config").joinpath("f_manager")
            elif self._platform in ("windows",):
                user_dir = Path(os.environ["APPDATA"]).joinpath("f_manager")

            user_path = user_dir.joinpath("default.yaml")

            if not user_path.exists():
                if not default_path.exists():
                    raise FileNotFoundError(f"""Could not found default config file ({default_path}).
Reinstall package or create one""")

                os.makedirs(user_path.parent)
                shutil.copy(default_path, user_path)
            self._filename = user_path

            yaml.SafeLoader.add_constructor("!join", join_constructor)

            with self._filename.open() as stream:
                self._config = yaml.safe_load(stream)

    @property
    def loglevel(self):
        lev = self._config.get('loglevel')

        if lev not in ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'):
            raise ValueError(f"{lev} is not a valid loglevel")

        return lev

    @property
    def base_dir(self):
        _dir = expand_path(self._config.get("game").get('base_dir'))

        if not _dir.exists():
            raise FileNotFoundError(f"{_dir} is not found. Check if it exists or change configuration")

        return _dir

    @property
    def mods_dir(self):
        _dir = expand_path(self._config.get("game").get('mods_dir'))

        if not _dir.exists():
            raise FileNotFoundError(f"{_dir} is not found. Check if it exists or change configuration")

        return _dir

    @property
    def mods_file(self):
        _dir = self.mods_dir
        _filename = _dir.joinpath("mod-list.json")

        if not _filename.exists():
            raise FileNotFoundError(f"{_filename} is not found. Check if it exists or change configuration")

        return _filename

    @property
    def user_data_dir(self):
        _dir = expand_path(self._config.get("user").get("base_dir"))

        if not _dir.exists():
            os.makedirs(_dir)

        return _dir

    @property
    def profiles_dir(self):
        _dir = self.user_data_dir.joinpath("profiles")

        if not _dir.exists():
            os.makedirs(_dir)

        return _dir

    @property
    def username(self) -> str | None:
        _username = self._config.get("auth").get("username")

        if not _username:
            with self.base_dir.joinpath("player-data.json").open() as f:
                _username = json.load(f).get("service-username")

        return _username

    @property
    def token(self):
        """

        TODO:
            - write token on login to user data directory

        """

        _token = self._config.get("auth").get("token")

        if not _token:
            with self.base_dir.joinpath("player-data.json").open() as f:
                _token = json.load(f).get("service-token")

        return _token

    @property
    def password(self):
        return self._config.get("auth").get("password")

    def get_raw(self):
        return self._config


config = Config()
