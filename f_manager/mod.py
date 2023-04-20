from __future__ import annotations

import json
import pathlib
import urllib.parse as urlparse
import zipfile
from difflib import SequenceMatcher
from typing import Any, Literal, Iterable

import requests
from packaging.version import Version

from f_manager import config, exceptions
from f_manager.helpers import friendly_list, parse_dependency
from f_manager.logger import logger


class Mod:
    """A class to represent a mod.

    Attributes:
        name (str): Name of the mod

    TODO:
        - check for using config values and add foolproof
        - refactor and reformat
        - add if mod is not dependents of `base` but dependents on factorio version
        - remove orphans?

    """

    def __init__(self, name: str, filename: str | pathlib.Path = None):
        """Initializes a Mod instance with the given instance attributes.

        Args:
            name (str): name of the mod
        """

        if not isinstance(name, str):
            raise TypeError("'name' should be of type 'str'")

        self.name = name
        self._filename = None
        self._info = None

        # name
        # version
        # title
        # author
        # dependencies
        # description
        # factorio_version
        # homepage

    def clear(self):
        self._filename = None
        self._info = None

    @classmethod
    def name(cls, mod: Mod) -> str:
        """Class method to use with 'map' or something

        Args:
            mod (Mod): Mod to get the name

        Returns:
            str: name of the mod

        """

        if not isinstance(mod, Mod):
            raise TypeError("The object must be an instance of Mod or its subclass")

        return mod.name

    @property
    def filename(self) -> pathlib.Path | None:
        """
        Note:
            if self.name == "base" returns the path to info.json and not the path to the zip archive

        Returns:
            pathlib.Path: Path to mod file if exists, None otherwise
        """

        if self._filename:
            return self._filename

        if self.name == "base":
            self._filename = (
                config.base_dir
                .joinpath("data")
                .joinpath("base")
                .joinpath("info.json")
            )
        else:
            if not config.mods_dir.joinpath("mods").joinpath("").is_file():
                raise exceptions.FileNotFoundException(config.mods_file)

            for file in config.mods_file.parent.rglob("*.zip"):
                if file.stem.rsplit("_", 1)[0] == self.name:
                    self._filename = file
                    break

        return self._filename

    @property
    def info(self) -> dict | None:
        """Parse info.json from zip archive

        Note:
            if self.name == "base" parsing clear json and zip archive otherwise

        Returns:
            dict: Dictionary containing all mod info, None otherwise
        """
        if not self.filename:
            return None

        if self._info:
            return self._info

        if self.name == "base":
            with self.filename.open() as f:
                self._info: dict = json.load(f)
        else:
            with zipfile.ZipFile(self.filename) as archive:
                info_json_path = list(
                    filter(
                        lambda zipinfo: "info.json" in zipinfo.filename,
                        archive.filelist
                    )
                )[0].filename

                self._info = json.loads(
                    archive.read(info_json_path).decode("utf-8")
                )

        return self._info

    @property
    def version(self) -> Version:
        """Version: version of the mod"""
        if self._info:
            return Version(self.info.get("version")) if self.filename else None
        elif self.filename:
            return Version(self.filename.stem.rsplit("_", 1)[-1])

    @property
    def factorio_version(self) -> str:
        return self.info.get("factorio_version") if self.filename else None

    @property
    def title(self) -> str:
        """str: extended name of the mod"""
        return self.info.get("title") if self.filename else None

    @property
    def author(self) -> str:
        """str: author of the mod"""
        return self.info.get("author") if self.filename else None

    @property
    def contact(self) -> str:
        """str: mod authors contact"""
        return self.info.get("contact") if self.filename else None

    @property
    def homepage(self) -> str:
        """str: homepage of the mod"""
        return self.info.get("homepage") if self.filename else None

    @property
    def description(self) -> str:
        """str: description of the mod"""
        return self.info.get("description") if self.filename else None

    @property
    def size(self) -> int | None:
        """int: size of the mod (bytes) if mod exists, None otherwise"""
        if not self.filename:
            return None

        return None if self.name == "base" else self.filename.stat().st_size

    @property
    def dependencies(self) -> list[dict[str, str | Version]]:
        """
        Example:
            {
                "name": "MOD_NAME",

                "category": "MOD_CATEGORY",

                "min_version": "MOD_MIN_VERSION",

                "max_version": "MOD_MAX_VERSION",

                "version": "MOD_VERSION",

                "from_min_version": "MOD_MIN_VERSION",

                "to_max_version": "MOD_MAX_VERSION",
            }

        Note:
            `min_version`, `max_version`, `from_min_version`, `to_max_version` and `version` may be missing
            if nobody gives a fuck which version of the mod

            MOD_CATEGORY: ["optional", "conflict", "parent", "require"]

            min_version: >=

            from_min_version: >

            max_version: <=

            to_max_version: <

            version: ==

        Returns:
            list[dict[str, str | Version]]: dependencies dictionary

        TODO:
            - save results

        """
        return [
            parse_dependency(dep_raw)
            for dep_raw in self.info.get("dependencies")
        ] if self.info.get("dependencies") else []

    @property
    def depends_on(self) -> list[dict[str, str]]:
        """list[dict[str, str]]: of dependencies"""
        return list(
            filter(
                lambda dep: dep.get("category") == "require",
                self.dependencies
            )
        )

    @property
    def optional_deps(self) -> list[dict[str, str]]:
        """list[dict[str, str]]: of dependencies"""
        return list(
            filter(
                lambda dep: dep.get("category") == "optional",
                self.dependencies
            )
        )

    @property
    def required_by(self):
        """list[Mod]: of dependencies

        TODO:
            - save results

        """

        deps = []

        for mod in ModController().downloaded:
            deps.extend(
                mod
                for dependency in mod.dependencies
                if dependency.get("category") == "require"
                and dependency.get("name") == self.name
            )

        return deps

    @property
    def optional_for(self):
        """list[Mod]: of dependencies

        TODO:
            - save results

        """

        deps = []

        for mod in ModController().downloaded:
            deps.extend(
                mod
                for dependency in mod.dependencies
                if dependency.get("category") == "optional"
                and dependency.get("name") == self.name
            )

        return deps

    @property
    def conflicts_with(self) -> list[dict[str, str]]:
        """list[dict[str, str]]: of dependencies"""

        return list(
            filter(
                lambda dep: dep.get("category") == "conflict",
                self.dependencies
            )
        )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"""<class '{__class__.__name__}' name: '{self.name}'>"""


SearchOrders = Literal["updated", "downloaded"]
_VALID_SEARCH_ORDERS = {"updated", "downloaded"}


class ModController:
    """Helper class to work with lots of mods"""

    def __init__(self):
        pass

    @classmethod
    def remove(cls, mod: Mod | str, with_required_by=False, with_depends_on=False, force=False):
        """Removes the mod and his dependencies

        Note:
            Method doesn't remove ``depends_on`` list but returns it in the end

        Args:
            mod: mod to remove
            with_required_by (bool): remove with mods from ``required_by`` list (ignoring ``DependencyRemove``
                exception)
            force (bool): ignore all and remove

        Returns:
            list[Mod]: a list of possibly orphaned mods on which ``mod`` depended

        Raises:
            BaseModRemoveError: If mod.name is `base`
            DependencyRemove: If some of downloaded mods requires ``mod``

        """

        mod = cls._validate_mod(mod)

        if mod.name == "base":
            raise exceptions.BaseModRemoveError()

        if not mod.filename:
            logger.warning(f"'{mod.name}' is not exists. Ignoring")
            return

        required_by = mod.required_by
        if required_by and not with_required_by and not force:
            raise exceptions.DependencyRemove(
                f"'{mod.name}' is required by "
                f"{friendly_list(map(lambda _mod: _mod.name, required_by), 'and')}"
            )

        depends_on = list(map(lambda m: Mod(m.get("name")), mod.depends_on))

        if required_by and with_required_by:
            for dep in required_by:
                depends_on.extend(cls.remove(dep, with_required_by))

        mod.filename.unlink()

        with config.mods_file.open() as f:
            mod_list = json.load(f)

        mod_list["mods"] = list(filter(lambda m: m.get("name") != mod.name, mod_list["mods"]))
        with config.mods_file.open("w") as f:
            json.dump(mod_list, f, ensure_ascii=False, indent=4)

        mod.clear()

        depends_on = list(filter(lambda m: m.name not in [mod.name, 'base'], depends_on))
        deps_names_set = set(map(Mod.name, depends_on))

        return sorted(list(map(Mod, deps_names_set)), key=lambda m: m.name)

    @classmethod
    def download(cls, mod: str | Mod, reinstall=False, with_dependencies=True, soft=False):
        """Download mod from mod portal with all necessary dependencies

        Args:
            mod: mod to download
            reinstall (bool): reinstall the mod (``ModAlreadyExistsError`` exception ignoring)
            with_dependencies (bool): reinstall the mod with all his dependencies
            soft (bool): do not raise exception but print logging

        Returns:
            None

        Raises:
            TypeError: If using wrong argument types
            ModAlreadyExistsError: If mod already exists
            FileNotFoundException: If config file does not exist
            APIcallError: Some troubles with connecting to the server

        TODO:
            - optimize for cycle to not trying to download the same mod thousand times
            - check for current factorio/base version with compatible mod version
            - validate checksum
            - split into smaller methods

        """

        mod = cls._validate_mod(mod)

        if not isinstance(reinstall, bool):
            logger.exception("'reinstall' argument should be of type 'bool'")
            raise TypeError("'reinstall' argument should be of type 'bool'")

        # if not isinstance(with_dependencies, bool):
        #     logger.exception("'with_dependencies' argument should be of type 'bool'")
        #     raise TypeError("'with_dependencies' argument should be of type 'bool'")

        if mod.name == "base":
            return

        if mod.filename and not reinstall:
            logger.exception(f"ModAlreadyExistsError exception with {mod.name}")
            if not soft:
                raise exceptions.ModExistsError(mod.name)
            else:
                return

        # TODO check player_data.json account data if user is not logged in or doesn't have full account

        if not config.game_folder.is_dir():
            raise exceptions.FileNotFoundException(config.game_folder)

        with config.game_folder.joinpath("player-data.json").open() as f:
            player_data = json.load(f)
            username, token = player_data.get('service-username'), player_data.get('service-token')

        response = cls._api_mods_full(mod.name)
        if response.status_code != 200:
            logger.exception(f"APIcallError with {response.status_code}")
            if not soft:
                raise exceptions.APIcallError(response)
            else:
                return

        # TODO will be refactored taking into account version compatibility
        release = response.json().get('releases')[-1]

        download_url, file_name = release.get("download_url"), release.get("file_name")

        url = f"https://mods.factorio.com/{download_url}?"
        url_params = {
            "username": username,
            "token": token
        }
        url = url + urlparse.urlencode(url_params)

        mod_response = requests.get(url)
        if mod_response.status_code != 200:
            logger.exception(f"APIcallError with {mod_response.status_code}")
            if not soft:
                raise exceptions.APIcallError(mod_response)
            else:
                return

        if not config.mods_file.parent.is_dir():
            raise exceptions.FileNotFoundException(config.mods_file.parent)

        if mod.filename:
            cls.remove(mod, force=True)

        with config.mods_file.parent.joinpath(file_name).open("wb") as f:
            f.write(mod_response.content)

        with config.mods_file.open() as f:
            mod_list = json.load(f)

        mod_list["mods"].append({"name": mod.name, "enabled": False})
        with config.mods_file.open("w") as f:
            json.dump(mod_list, f, ensure_ascii=False, indent=4)

        logger.info(f"'{mod}' has been {'reinstalled' if reinstall else 'downloaded'}")

        if with_dependencies:
            for dep in mod.depends_on + list(filter(lambda d: d.get("category") == "parent", mod.dependencies)):
                logger.info(f"Installing {dep.get('name')} from '{mod}'")
                cls.download(dep.get("name"), reinstall, with_dependencies, soft)

    def download_new(self, mod: str | Mod = None, mods: Iterable[str | Mod] = None, reinstall: bool = False):
        """

        check mod | list of mods dependencies and collect them to a list
        check for already installed
            if the same version as remote already installed then fuck it
        check for conflicts

        if mod already installed then reinstall (without dependencies and the same version)

        """

        if not mod and not mods:
            raise TypeError(f"{__class__.__name__}.download() missing 1 required argument: 'mod' or 'mods'")
        elif mod and mods:
            raise TypeError(f"{__class__.__name__}.download() takes only argument: 'mod' or 'mods' and not both "
                            f"together")

        if mod:
            if isinstance(mod, str):
                mod = Mod(mod)
            elif mod is not None:
                raise TypeError(f"mod must be Mod or a string, not {type(mod).__name__}")
            mods = [mod]
        elif mods:
            if not isinstance(mods, Iterable):
                raise TypeError(f"mods must be Iterable not {type(mods).__name__}")
            if all(map(lambda _mod: isinstance(_mod, str), mods)):
                mods = map(lambda mod_name: Mod(mod_name), mods)
            if not all(map(lambda _mod: isinstance(_mod, Mod), mods)):
                raise TypeError("mods must be Iterable[Mod] or Iterable[str]")

        # check if mod already installed
        for mod in mods:
            if mod.filename and not reinstall:
                raise exceptions.ModExistsError(f"{mod.name} already exists")
            elif not reinstall:
                pass

    @classmethod
    def _api_mods_full(cls, mod_name: str):
        """Call to mod portal API (mods/MOD_NAME/full)

        Args:
            mod_name: Name of the mod

        Returns:
            Response: Mod information

        """

        url = f"https://mods.factorio.com/api/mods/{mod_name}/full"

        return requests.get(url)

    @classmethod
    def update(cls, mod: Mod | str) -> Version | None:
        """Check for the new version of the mod

        Args:
            mod: The mod to update

        Returns:
            Version | None: The new version of the mod, or None otherwise

        TODO:
            - check for current factorio/base version with compatible mod version

        """

        mod = cls._validate_mod(mod)

        if mod.name == "base":
            return

        if not mod.filename:
            raise exceptions.ModNotFoundError(mod.name)

        response = cls._api_mods_full(mod.name)
        if response.status_code != 200:
            logger.exception(f"APIcallError with {response.status_code}")
            raise exceptions.APIcallError(response.status_code)

        new_version = Version(response.json().get("releases")[-1].get("version"))

        return new_version if new_version > mod.version else None

    @classmethod
    def upgrade(cls, mod: Mod | str):
        """Upgrade the mod

        Args:
            mod: The mod to upgrade

        Returns:
            None

        TODO:
            - optimize not to calling API twice for update and download

        """

        mod = cls._validate_mod(mod)

        if cls.update(mod):
            cls.download(mod, True)

    @classmethod
    def search(cls, query: str):  # sourcery skip: remove-unnecessary-cast
        """Search for mod containing ``query`` in `name`, `title`, `owner` and `summary`

        Note:
            Returns all of the mods.

            ! DO NOT USE OFTEN !

        Args:
            query: query to search

        Returns:
            list[dict[str, Any]]: Result Entry containing mod information.
            Result Entry docs: https://wiki.factorio.com/Mod_portal_API#Result_Entry
            (the most matches is in the end of the list)


        TODO:
            - choose category
            - prevent loading full list of mods
            - filter by current factorio version

        """

        if not isinstance(query, str):
            query = str(query)

        response = cls.call_api_mods(page_size="max")
        if response.status_code != 200:
            logger.exception(f"APIcallError with {response.status_code}")
            raise exceptions.APIcallError(response)

        api_mods: dict = response.json()

        # if not config.mods_file.parent.is_dir():
        #     raise exceptions.FileNotFoundException(config.mods_file.parent)

        # with config.mods_file.parent.joinpath("api_mods.json").open("w") as f:
        #     json.dump(response.json(), f, indent=4, ensure_ascii=False)

        # with config.mods_file.parent.joinpath("api_mods.json").open() as f:
        #     api_mods: dict = json.load(f)

        return cls._sort_query(query, api_mods.get("results"))

    @classmethod
    def _sort_query(cls, query: str, results: dict[str, Any]):
        """

        TODO:
            - check for original factorio sort order (or made better)
            - drop entities which are not needed at all (SequenceMatcher().radio() == 0 for example)

        """

        keys = [
            "name",
            "title",
            "owner",
            "summary"
        ]

        return sorted(
            results,
            key=lambda result: max(
                SequenceMatcher(
                    a=query.lower(),
                    b=result.get(key).lower()
                ).ratio()
                for key in keys
            )
        )

    @classmethod
    def call_api_mods(cls, **kwargs):
        """Calling to API

        Note:
            ``page`` argument must be greater than or equal to ``1``. Otherwise, page is forcibly assigned ``1``

            docs: https://wiki.factorio.com/Mod_portal_API

        Keyword args:
            hide_deprecated (bool): Only return non-deprecated mods

            page (int): Page number you would like to show. Makes it, so you can see a certain part of the list
                without getting detail on all
            page_size (int | Literal["max"]): The amount of results to show in your search
            sort (Literal["name", "created_at", "updated_at"]): Sort results by this property. Defaults to name when
                not defined. Ignored for ``page_size="max"`` queries
            sort_order (Literal["asc", "desc"]): Sort results ascending or descending. Defaults to descending when
                not defined. Ignored for ``page_size="max"`` queries
            namelist (str | list[str]): Return only mods that match the given names. Response will include
                ``releases`` instead of ``latest_release``
            version (packaging.version.Version | str): Only return non-deprecated mods compatible with this Factorio
                version

        Returns:
            Response: Response object

        Raises:
            KeyError: If there is unknown key in ``kwargs``
            TypeError: If illegal value type

        """

        url = "https://mods.factorio.com/api/mods"
        params = cls._validate_api_params(**kwargs)

        return requests.get(url, params=params)

    @classmethod
    def _validate_api_params(cls, **params):
        """Checking the use of the correct API parameters"""
        known_keys = [
            "hide_deprecated",
            "page",
            "page_size",
            "sort",
            "sort_order",
            "namelist",
            "version",
        ]

        if any(key not in known_keys for key in params):
            raise KeyError(f"API accepts only {friendly_list(known_keys, 'and')} keys")

        hide_deprecated = params.get("hide_deprecated")
        if hide_deprecated is not None:
            if not isinstance(hide_deprecated, bool):
                raise TypeError("'hide_deprecated' keyword argument has to be of type 'bool'")
            params["hide_deprecated"] = bool(hide_deprecated)

        page = params.get("page")
        if page is not None:
            if not isinstance(page, int):
                raise TypeError("'page' keyword argument has to be of type 'int'")
            if int(page) < 1:
                page = 1
            params["page"] = int(page)

        page_size = params.get("page_size")
        if page_size is not None:
            if (not isinstance(page_size, (int, str))) or (isinstance(page_size, str) and page_size != "max"):
                raise TypeError("'page_size' keyword argument has to be of type 'int' or Literal[\"max\"]")
            params["page_size"] = page_size

        sort = params.get("sort")
        if sort:
            if not isinstance(sort, str):
                raise TypeError("'sort' keyword argument has to be of type 'str'")
            elif sort not in ["name", "created_at", "updated_at"]:
                raise TypeError(
                    "'sort' keyword argument has to be of type Literal[\"name\", \"created_at\", \"updated_at\"]")
            params["sort"] = sort

        sort_order = params.get("sort_order")
        if sort_order:
            if sort_order not in ["asc", "desc"]:
                raise TypeError("'sort' keyword argument has to be of type Literal[\"asc\", \"desc\"]")
            params["sort_order"] = sort_order

        namelist = params.get("namelist")
        if namelist:
            if not isinstance(namelist, (list, str)):
                raise TypeError("'name_list' keyword argument has to be of type 'list'")
            if isinstance(namelist, list) and not all(isinstance(name, str) for name in namelist):
                raise TypeError("'name_list' elements has to be of type 'str'")
            if isinstance(namelist, str):
                namelist = [namelist]
            params["namelist"] = namelist

        version = params.get("version")
        if version:
            if not isinstance(version, (Version, str)):
                raise TypeError("'version' keyword argument has to be of type 'Version' or 'str'")
            params["version"] = version

        return params

    @classmethod
    def _validate_order(cls, order: str) -> str:
        if order not in _VALID_SEARCH_ORDERS:
            raise exceptions.InvalidSearchOrder(f"Valid search orders are {friendly_list(_VALID_SEARCH_ORDERS)}")
        return order

    @classmethod
    def _validate_mod(cls, mod: Mod | str) -> Mod:
        if not isinstance(mod, (Mod, str)):
            raise TypeError("'mod' argument should be of type 'Mod' or 'str'")

        if isinstance(mod, str):
            mod = Mod(mod)
        return mod

    @property
    def downloaded(self) -> Iterable[Mod]:
        with config.mods_file.open() as f:
            mods_list = json.load(f).get("mods")

        for mod_dict in mods_list:
            yield Mod(mod_dict.get("name"))
