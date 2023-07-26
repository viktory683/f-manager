# from __future__ import annotations

# import json
# import zipfile
# from typing import Any, Dict, Generator, Iterable, List, Optional

# from packaging.version import Version

# from f_manager_core import config
# from f_manager_core.factorio_api import FactorioAPIClient
# from f_manager_core.helpers import parse_dependencies, sort_query


class Mod:
    """A class to represent a mod.

    Attributes:
        name (str): Name of the mod

    TODO:
        - Add optional_for property (should return a list of installed mods that optionally requiring current mod)
        - The same with required_by
        - also optional_deps and depends_on but it will simply parse mod.info

    """  # noqa: E501

    def __init__(self, name: str):
        """Initializes a Mod instance with the given instance attributes.

        Args:
            name (str): name of the mo

        """

        if not isinstance(name, str):
            raise TypeError("'name' should be of type 'str'")

        self.name = name
        self.__exists = None
        self.__info = {}

    # @property
    # def exists(self) -> bool:
    #     if self.__exists is None:
    #         self.info
    #         return self.__exists

    #     return self.__exists

    # @property
    # def info(self) -> Dict[str, Any]:
    #     """Get or set the info property.

    #     The info property is retrieved from an archive file in the mods_dir. If the info property is not set, this method will load the info from the appropriate file or archive and then cache it for subsequent calls.

    #     The returned dictionary can contain the following keys:
    #     - name (str)
    #     - version (str)
    #     - title (str)
    #     - author (str)
    #     - contact (str)
    #     - description (str)
    #     - homepage (str)
    #     - factorio_version (str)
    #     - dependencies (list[str])

    #     Returns:
    #         dict: A dictionary containing the info of the object with the keys mentioned above.

    #     Raises:
    #         FileNotFoundError: If the info.json file or archive file is not found.
    #         json.JSONDecodeError: If the info.json file or archive file contains invalid JSON.

    #     """  # noqa: E501

    #     if self.__info:
    #         return self.__info

    #     zip_filename = next(
    #         (
    #             filename
    #             for filename in config.mods_dir.rglob("*.zip")
    #             if filename.stem.rsplit("_", 1)[0] == self.name
    #         ),
    #         None,
    #     )

    #     if not zip_filename:
    #         self.__exists = False
    #         return {}

    #     self.__exists = True

    #     with zipfile.ZipFile(zip_filename) as archive:
    #         info_path = next(
    #             (
    #                 zipinfo.filename
    #                 for zipinfo in archive.filelist
    #                 if "info.json" in zipinfo.filename
    #             ),
    #             None,
    #         )
    #         if not info_path:
    #             return {}

    #         text = archive.read(info_path).decode("utf8")

    #     self.__info = json.loads(text)
    #     return self.__info

    # @info.setter
    # def info(self, __value: dict):
    #     if not isinstance(__value, dict):
    #         raise ValueError("Value must be a dict")

    #     self.__info = __value

    # @property
    # def version(self) -> Optional[Version]:
    #     _version = self.info.get("version")
    #     return Version(_version) if _version else None

    # @property
    # def factorio_version(self) -> Optional[Version]:
    #     _version = self.info.get("factorio_version")
    #     return Version(_version) if _version else None

    # @property
    # def optional_for(self) -> Iterable[Mod]:
    #     return ModManager.find_optional_for(self)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"""<class '{__class__.__name__}' name: '{self.name}'>"""

    def __new__(cls, name):
        if cls is Mod:
            return super().__new__(BaseMod) if name == "base" else super().__new__(cls)


class BaseMod(Mod):
#     def __init__(self, *args, **kwargs):
#         super().__init__("base")

#     @property
#     def info(self) -> Dict[str, Any]:
#         """Get or set the info property.

#         The info property is retrieved from the info.json file located in the 'base' directory. If the info property is not set, this method will load the info from the appropriate file or archive and then cache it for subsequent calls.

#         The returned dictionary can contain the following keys:
#         - name (str)
#         - version (str)
#         - title (str)
#         - author (str)
#         - contact (str)
#         - homepage (str)
#         - dependencies (List)

#         Returns:
#             dict: A dictionary containing the info of the object with the keys mentioned above.

#         Raises:
#             FileNotFoundError: If the info.json file or archive file is not found.
#             json.JSONDecodeError: If the info.json file or archive file contains invalid JSON.

#         """  # noqa: E501

#         if self._info:
#             return self._info

#         with config.base_dir.joinpath("data").joinpath("base").joinpath(
#             "info.json"
#         ).open() as f:
#             text = f.read()

#         self._info = json.loads(text)
#         return self._info

    # @property
    # def factorio_version(self) -> Optional[Version]:
    #     return self.version

    def __repr__(self) -> str:
        return f"""<class '{__class__.__name__}' name: '{self.name}'>"""


# SearchOrders = Literal["updated", "downloaded"]
# _VALID_SEARCH_ORDERS = {"updated", "downloaded"}


class ModManager:
    """Helper class to work with lots of mods"""

    # @classmethod
    # def remove(cls, mod: Mod | str, with_required_by=False, with_depends_on=False, force=False):
    #     """Removes the mod and his dependencies

    #     Note:
    #         Method doesn't remove ``depends_on`` list but returns it in the end

    #     Args:
    #         mod: mod to remove
    #         with_required_by (bool): remove with mods from ``required_by`` list (ignoring ``DependencyRemove``
    #             exception)
    #         force (bool): ignore all and remove

    #     Returns:
    #         list[Mod]: a list of possibly orphaned mods on which ``mod`` depended

    #     Raises:
    #         BaseModRemoveError: If mod.name is `base`
    #         DependencyRemove: If some of downloaded mods requires ``mod``

    #     """

    #     mod = cls._validate_mod(mod)

    #     if mod.name == "base":
    #         raise exceptions.BaseModRemoveError()

    #     if not mod.filename:
    #         logger.warning(f"'{mod.name}' is not exists. Ignoring")
    #         return

    #     required_by = mod.required_by
    #     if required_by and not with_required_by and not force:
    #         raise exceptions.DependencyRemove(
    #             f"'{mod.name}' is required by "
    #             f"{friendly_list(map(lambda _mod: _mod.name, required_by), 'and')}"
    #         )

    #     depends_on = list(map(lambda m: Mod(m.get("name")), mod.depends_on))

    #     if required_by and with_required_by:
    #         for dep in required_by:
    #             depends_on.extend(cls.remove(dep, with_required_by))

    #     mod.filename.unlink()

    #     with config.mods_file.open() as f:
    #         mod_list = json.load(f)

    #     mod_list["mods"] = list(filter(lambda m: m.get("name") != mod.name, mod_list["mods"]))
    #     with config.mods_file.open("w") as f:
    #         json.dump(mod_list, f, ensure_ascii=False, indent=4)

    #     mod.clear()

    #     depends_on = list(filter(lambda m: m.name not in [mod.name, 'base'], depends_on))
    #     deps_names_set = set(map(Mod.name, depends_on))

    #     return sorted(list(map(Mod, deps_names_set)), key=lambda m: m.name)

    # @classmethod
    # def download(cls, mod: str | Mod, reinstall=False, with_dependencies=True, soft=False):
    #     """Download mod from mod portal with all necessary dependencies

    #     Args:
    #         mod: mod to download
    #         reinstall (bool): reinstall the mod (``ModAlreadyExistsError`` exception ignoring)
    #         with_dependencies (bool): reinstall the mod with all his dependencies
    #         soft (bool): do not raise exception but print logging

    #     Returns:
    #         None

    #     Raises:
    #         TypeError: If using wrong argument types
    #         ModAlreadyExistsError: If mod already exists
    #         FileNotFoundException: If config file does not exist
    #         APIcallError: Some troubles with connecting to the server

    #     TODO:
    #         - optimize for cycle to not trying to download the same mod thousand times
    #         - check for current factorio/base version with compatible mod version
    #         - validate checksum
    #         - split into smaller methods

    #     """

    #     mod = cls._validate_mod(mod)

    #     if not isinstance(reinstall, bool):
    #         logger.exception("'reinstall' argument should be of type 'bool'")
    #         raise TypeError("'reinstall' argument should be of type 'bool'")

    #     # if not isinstance(with_dependencies, bool):
    #     #     logger.exception("'with_dependencies' argument should be of type 'bool'")
    #     #     raise TypeError("'with_dependencies' argument should be of type 'bool'")

    #     if mod.name == "base":
    #         return

    #     if mod.filename and not reinstall:
    #         logger.exception(f"ModAlreadyExistsError exception with {mod.name}")
    #         if not soft:
    #             raise exceptions.ModExistsError(mod.name)
    #         else:
    #             return

    #     # TODO check player_data.json account data if user is not logged in or doesn't have full account

    #     if not config.game_folder.is_dir():
    #         raise exceptions.FileNotFoundException(config.game_folder)

    #     with config.game_folder.joinpath("player-data.json").open() as f:
    #         player_data = json.load(f)
    #         username, token = player_data.get('service-username'), player_data.get('service-token')

    #     response = cls._api_mods_full(mod.name)
    #     if response.status_code != 200:
    #         logger.exception(f"APIcallError with {response.status_code}")
    #         if not soft:
    #             raise exceptions.APIcallError(response)
    #         else:
    #             return

    #     # TODO will be refactored taking into account version compatibility
    #     release = response.json().get('releases')[-1]

    #     download_url, file_name = release.get("download_url"), release.get("file_name")

    #     url = f"https://mods.factorio.com/{download_url}?"
    #     url_params = {
    #         "username": username,
    #         "token": token
    #     }
    #     url = url + urlparse.urlencode(url_params)

    #     mod_response = requests.get(url)
    #     if mod_response.status_code != 200:
    #         logger.exception(f"APIcallError with {mod_response.status_code}")
    #         if not soft:
    #             raise exceptions.APIcallError(mod_response)
    #         else:
    #             return

    #     if not config.mods_file.parent.is_dir():
    #         raise exceptions.FileNotFoundException(config.mods_file.parent)

    #     if mod.filename:
    #         cls.remove(mod, force=True)

    #     with config.mods_file.parent.joinpath(file_name).open("wb") as f:
    #         f.write(mod_response.content)

    #     with config.mods_file.open() as f:
    #         mod_list = json.load(f)

    #     mod_list["mods"].append({"name": mod.name, "enabled": False})
    #     with config.mods_file.open("w") as f:
    #         json.dump(mod_list, f, ensure_ascii=False, indent=4)

    #     logger.info(f"'{mod}' has been {'reinstalled' if reinstall else 'downloaded'}")

    #     if with_dependencies:
    #         for dep in mod.depends_on + list(filter(lambda d: d.get("category") == "parent", mod.dependencies)):
    #             logger.info(f"Installing {dep.get('name')} from '{mod}'")
    #             cls.download(dep.get("name"), reinstall, with_dependencies, soft)

    # def download_new(self, mod: str | Mod = None, mods: Iterable[str | Mod] = None, reinstall: bool = False):
    #     """

    #     check mod | list of mods dependencies and collect them to a list
    #     check for already installed
    #         if the same version as remote already installed then fuck it
    #     check for conflicts

    #     if mod already installed then reinstall (without dependencies and the same version)

    #     """

    #     if not mod and not mods:
    #         raise TypeError(f"{__class__.__name__}.download() missing 1 required argument: 'mod' or 'mods'")
    #     elif mod and mods:
    #         raise TypeError(f"{__class__.__name__}.download() takes only argument: 'mod' or 'mods' and not both "
    #                         f"together")

    #     if mod:
    #         if isinstance(mod, str):
    #             mod = Mod(mod)
    #         elif mod is not None:
    #             raise TypeError(f"mod must be Mod or a string, not {type(mod).__name__}")
    #         mods = [mod]
    #     elif mods:
    #         if not isinstance(mods, Iterable):
    #             raise TypeError(f"mods must be Iterable not {type(mods).__name__}")
    #         if all(map(lambda _mod: isinstance(_mod, str), mods)):
    #             mods = map(lambda mod_name: Mod(mod_name), mods)
    #         if not all(map(lambda _mod: isinstance(_mod, Mod), mods)):
    #             raise TypeError("mods must be Iterable[Mod] or Iterable[str]")

    #     # check if mod already installed
    #     for mod in mods:
    #         if mod.filename and not reinstall:
    #             raise exceptions.ModExistsError(f"{mod.name} already exists")
    #         elif not reinstall:
    #             pass

    # @classmethod
    # def update(cls, mod: Mod | str) -> Version | None:
    #     """Check for the new version of the mod

    #     Args:
    #         mod: The mod to update

    #     Returns:
    #         Version | None: The new version of the mod, or None otherwise

    #     TODO:
    #         - check for current factorio/base version with compatible mod version

    #     """

    #     mod = cls._validate_mod(mod)

    #     if mod.name == "base":
    #         return

    #     if not mod.filename:
    #         raise exceptions.ModNotFoundError(mod.name)

    #     response = cls._api_mods_full(mod.name)
    #     if response.status_code != 200:
    #         logger.exception(f"APIcallError with {response.status_code}")
    #         raise exceptions.APIcallError(response.status_code)

    #     new_version = Version(response.json().get("releases")[-1].get("version"))

    #     return new_version if new_version > mod.version else None

    # @classmethod
    # def upgrade(cls, mod: Mod | str):
    #     """Upgrade the mod
    #
    #     Args:
    #         mod: The mod to upgrade
    #
    #     Returns:
    #         None
    #
    #     TODO:
    #         - optimize not to calling API twice for update and download
    #
    #     """
    #
    #     mod = cls._validate_mod(mod)
    #
    #     if cls.update(mod):
    #         cls.download(mod, True)

    # @classmethod
    # def find_required_by(cls, mod: Mod) -> Iterable[Mod]:
    #     # TODO: extract common part from here and `find_optional_for`

    #     if not mod.exists:
    #         return None

    #     mod_list = cls.list()
    #     for _mod in mod_list:
    #         mod_deps = _mod.info.get("dependencies")
    #         if mod_deps:
    #             mandatory, *_ = parse_dependencies(mod_deps)
    #             if any(mod.name == dep[0] for dep in mandatory):
    #                 yield _mod

    # @classmethod
    # def find_optional_for(cls, mod: Mod) -> Iterable[Mod]:
    #     if not mod.exists:
    #         return None

    #     mod_list = cls.list()
    #     for _mod in mod_list:
    #         mod_deps = _mod.info.get("dependencies")
    #         if mod_deps:
    #             _, optional, *_ = parse_dependencies(mod_deps)
    #             if any(mod.name == dep[0] for dep in optional):
    #                 yield _mod

    # @classmethod
    # def search(cls, query: str) -> List[Dict[str, Any]]:
    #     """Search for mod containing ``query`` in `name`, `title`, `owner` and `summary`

    #     Note:
    #         Returns all of the mods.

    #     Args:
    #         query: query to search

    #     Returns:
    #         list[dict[str, Any]]: Result Entry containing mod information.
    #         Result Entry docs: https://wiki.factorio.com/Mod_portal_API#Result_Entry
    #         (the most matches is in the end of the list)


    #     TODO:
    #         - choose category
    #         - filter by current factorio version

    #     """

    #     mods = FactorioAPIClient.get_mods(page_size="max")
    #     if not mods:
    #         return []

    #     mods_list = mods.get("results")
    #     return sort_query(query, mods_list) if mods_list else []

    # @classmethod
    # def list(cls) -> Iterable[Mod]:
    #     mods_list = {
    #         filename.stem.rsplit("_", 1)[0]
    #         for filename in config.mods_dir.rglob("*.zip")
    #     }

    #     yield Mod("base")

    #     for mod_name in sorted(mods_list):
    #         yield Mod(mod_name)
