"""

Mod
> common stuff

LocalMod
> locally installed mod

- remove
- update
- upgrade


RemoteMod
> not installed locally mod

- download
- install

BaseMod
> base factorio mod

- ...

"""

from abc import abstractmethod, ABC
import json

from typing import Iterable, Optional
import zipfile

from f_manager_core import config
from f_manager_core.exceptions import BrokenModException, ModNotFoundError


class Mod(ABC):
    """Base class for mod classes"""

    name: str
    version: str
    title: str
    author: str
    contact: Optional[str] = None
    homepage: Optional[str] = None
    description: Optional[str] = None
    factorio_version: Optional[str] = None
    dependencies: Optional[Iterable[str]] = ("base",)

    def __init__(self) -> None:
        self.update_from_json(self.get_mod_info_json())

    def update_from_json(self, json_data: dict):
        for key, value in json_data.items():
            self.__dict__[key] = value

    @abstractmethod
    def get_mod_info_json(self) -> dict:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


class BaseMod(Mod):
    """Base mod class to avoid using of unacceptable methods"""

    def __init__(self) -> None:
        self.name = "base"
        super().__init__()

    def get_mod_info_json(self) -> dict:
        """
        docstring
        """
        json_path = config.factorio.data_dir.joinpath("base").joinpath("info.json")
        with json_path.open() as f:
            return json.load(f)

    def __repr__(self) -> str:
        return f"BaseMod(version='{self.version}', title='{self.title}', author='{self.author}', contact='{self.contact}', homepage='{self.homepage}', description='{self.description}', factorio_version='{self.factorio_version}', dependencies='{self.dependencies}')"


class LocalMod(Mod):
    """Regular mod class"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.file = None
        super().__init__()

    def get_mod_info_json(self) -> dict:
        """
        docstring
        """

        zip_file = next(
            (
                mod_file
                for mod_file in filter(
                    lambda file: file.suffix == ".zip",
                    config.factorio.mods_dir.iterdir(),
                )
                if mod_file.stem.split("_")[0] == self.name
            ),
            None,
        )
        if zip_file is None:
            raise ModNotFoundError(self.name)

        with zipfile.ZipFile(zip_file) as archieve:
            info_json_file = next(
                (
                    file
                    for file in archieve.filelist
                    if file.filename.endswith("info.json")
                ),
                None,
            )
            if info_json_file is None:
                raise BrokenModException(
                    f"Could not find 'info.json' file in '{self.name}' mod"
                )

            with archieve.open(info_json_file) as mod_info:
                return json.load(mod_info)

    def remove(self):
        """should remove a mod with his deps or not if it needed (returning Iterable of removing mods of RemoteMod)"""
        raise NotImplementedError

    def update(self):
        """should return something like status if update is available or update information (like link to a new version)
        or a list of updatable mods
        """
        raise NotImplementedError

    def upgrade(self):
        """should upgrade the current mod to a new version takes as an argument something like info for upgrading"""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"Mod(name='{self.name}', version='{self.version}', title='{self.title}', author='{self.author}', contact='{self.contact}', homepage='{self.homepage}', description='{self.description}', factorio_version='{self.factorio_version}', dependencies='{self.dependencies}')"


class RemoteMod(Mod):
    def __init__(self, name: str) -> None:
        super().__init__()

    def download(self):
        """should just download new version of mod to cache dir"""
        raise NotImplementedError

    def install(self):
        """check all nesessery info (like deps) then download mod and install it to game dir
        (returning Iterable of LocalMod's)"""
        raise NotImplementedError

    def get_mod_info_json(self):
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError


def gmod(name: Optional[str] = None) -> LocalMod | BaseMod | RemoteMod:
    """Something like factory (Get MOD)

    Args:
        name (Optional[str], optional): Name of the mod. Defaults to None.

    Returns:
        LocalMod | BaseMod | RemoteMod: object representing the mod
    """
    if name and name != "base":
        return (
            LocalMod(name) if name in get_locally_installed_mods() else RemoteMod(name)
        )
    return BaseMod()


def get_locally_installed_mods() -> Iterable[str]:
    """Scans game's mods direectory for all zip files

    Returns:
        Iterable[str]: Iterable by strings of mods names
    """
    for file in filter(lambda f: f.suffix == ".zip", config.factorio.mods_dir.iterdir()):
        yield file.stem.split("_")[0]
