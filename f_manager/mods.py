import json
import pathlib
import urllib.parse as urlparse
import zipfile
from typing import Generator

import requests
from bs4 import BeautifulSoup

from f_manager import config, exceptions
from f_manager.helpers import classproperty, parse_dependency
from f_manager.logger import logger
from f_manager.version import Version


class Mod:
    """A class to represent a mod.

    Attributes:
        name (str): name of the mod
        enabled (bool): special info for the profile

    TODO:
        * check for using config values and add foolproof
        * refactor and reformat
        * add if mod is not dependents of `base` but dependents on factorio version
        * remove orphans?
    """

    def __init__(self, name, enabled: bool = True):
        """Creates Mod object

        Args:
            name (str): name of the mod
            enabled (bool, optional): special info for the profile
        """
        self.name = name
        self.enabled = enabled
        self._downloaded = None
        self._version = None
        self._description = None
        self._name_extended = None
        self._has_new_version = None
        self._dependencies = {
            "require": [],
            "optional": [],
            'conflict': [],
            "parent": []
        }
        self._size = None
        self._filename = None
        self._info = None

    @property
    def downloaded(self) -> bool:
        """bool: True if mod exists in mods directory, False otherwise"""
        return bool(self.filename) if self.name != "base" else True

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
            if not config.game_folder.is_dir():
                raise exceptions.FileNotFoundException(config.game_folder)

            self._filename = (
                config.game_folder
                .joinpath("data")
                .joinpath("base")
                .joinpath("info.json")
            )
        else:
            if not config.mods_file.is_file():
                raise exceptions.FileNotFoundException(config.mods_file)

            for file in config.mods_file.parent.rglob("*.zip"):
                if file.stem.startswith(self.name):
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
        return Version(self.info.get("version")) if self.filename else None

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
            `min_version`, `max_version`, `from_min_version`, `to_max_version` and `version` may be missing if nobody gives a fuck which version of the mod

            MOD_CATEGORY: ["optional", "conflict", "parent", "require"]

            min_version: >=

            from_min_version: >

            max_version: <=

            to_max_version: <

            version: ==

        Returns:
            list[dict[str, str | Version]]: dependencies dictionary

        TODO:
            * save results
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
            * save results
        """

        deps = []

        for mod in Mod.downloaded_mods:
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
            * save results
        """

        deps = []

        for mod in Mod.downloaded_mods:
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

    def _api_mod_full_info(self):
        """Call to mods.factorio.com for full mod info

        Returns:
            Response: JSON information
        """
        return

        mods_url = "https://mods.factorio.com/api/mods"
        mod_url = f"{mods_url}/{self.name}"
        mod_full_url = f"{mod_url}/full"

        return requests.get(mod_full_url)

    def download(self, version: str = None, release_json=None):
        """Download mod from mod portal

        Args:
            version (str, optional): version of the mod
            release_json (dict, optional): release from `mods.factorio.com/api/mods/MOD_NAME`

        Returns:
            None

        TODO:
            * update mod-list.json with {"name": "mod.name", "enabled": False}
            * redo to match new dependencies format
            * downloads mod, his parents and requirements
        """
        return

        if self.downloaded:
            raise exceptions.ModAlreadyExistsError(self.name)

        if not release_json:
            response = self._api_mod_full_info()
            if response.status_code != 200:
                logger.warning(
                    f"""Could not download. Server is not responding. \
Status code: {response.status_code}""")
                return

            response_json = response.json()
            releases = response_json["releases"]
            if version is None:
                requested_release = releases[-1]
            else:
                for release in releases:
                    if version == release["version"]:
                        requested_release = release
                        break
                else:
                    raise exceptions.VersionNotFoundError(self.name, version)
        else:
            requested_release = release_json
        download_url = requested_release["download_url"]
        file_name = requested_release["file_name"]

        with config.game_folder.joinpath("player-data.json").open() as f:
            player_data = json.load(f)
            # TODO write checks if user does not have full account or not logged in
            username = player_data["service-username"]
            token = player_data["service-token"]

        url = f"https://mods.factorio.com/{download_url}?"
        url_params = {
            "username": username,
            "token": token
        }
        url = url + urlparse.urlencode(url_params)
        with config.mods_file.parent.joinpath(file_name).open("wb") as f:
            f.write(requests.get(url).content)

        self._downloaded = True
        self._version = requested_release["version"]

        logger.info(f"'{self.name}_{self.version}' successfully installed")

        for mod in self.dependencies["parent"] + self.dependencies["require"]:
            if not mod.downloaded:
                mod.download()

    def update(self) -> dict | None:
        """Check for the new version of the mod

        Returns:
            dict | None: decoded JSON release
        """
        return

        if not self.downloaded:
            raise exceptions.ModNotFoundError(self.name)

        if self._has_new_version:
            return self._has_new_version

        response = self._api_mod_full_info()
        if response.status_code != 200:
            logger.warning(
                f"""Could not download. Server is not responding. \
Status code: {response.status_code}""")
            return

        releases = response.json()["releases"]
        if self.version == releases[-1]["version"]:
            self._has_new_version = None

        self._has_new_version = releases[-1]

        return self._has_new_version

    def upgrade(self):
        """Updates the version of the mod and downloads it

        Returns:
            None
        """
        return

        if not (new_release := self.update()):
            logger.warning(
                f"The latest version of '{self.name}' already installed")
            return

        old_version = self.version
        self.remove()
        self.download(release_json=new_release)
        logger.info(
            f"""'{self.name}' successfully upgraded \
('{old_version}' -> '{self.version}')"""
        )

    def remove(self, remove_with_required_by=False):
        """Removes the mod with his dependencies

        Args:
            remove_with_required_by (bool): Whether to remove the dependencies

        Note:```
            status codes:
                ``0``: successful removed

                ``1``: trying to remove base mod (ignoring)

                ``2``: mod don't exist and nothing to remove (ignoring)

                ``3``: mod is required by other mods (can be ignored by ``remove_with_required_by`` flag)

                ``4``: mod dependency is required by other mod


        Returns:
            int: operation status code

        TODO:
            * redo to match new dependencies format
            * delete mod with required_by
        """

        return

        if self.name == "base":
            return 1

        if not self.filename:
            logger.warning(f"'{self.name}' wasn't downloaded. Ignoring")
            return 2

        if self.required_by and not remove_with_required_by:
            return 3

        if any(map(lambda mod: Mod(mod.get("name")).required_by, self.depends_on)):
            return 4

        for dep_mod in self.required_by:
            dep_mod.remove()

        for mod_file in config.mods_file.parent.rglob("*.zip"):
            if mod_file.stem.rsplit("_", 1)[0] == self.name:
                mod_file.unlink()
                logger.info(f"'{self.name}' mod was removed")
                break

        self._downloaded = False

        for mod in Mod.downloaded_mods:
            # delete all mods that required self.name
            # or those that self.name hard required

            # clear all parents and hard children
            if (
                    self.name in map(
                        lambda m: m.name,
                        mod.dependencies["require"]
                    )
                    or self.name in map(
                        lambda m: m.name,
                        mod.dependencies["parent"]
                    )
            ) and mod.downloaded:
                mod.remove()

        # clear all orphaned
        for dependency in self.dependencies["require"]:
            for downloaded_mod in Mod.downloaded_mods:
                if dependency.name in map(
                        lambda m: m.name,
                        (
                            downloaded_mod.dependencies["require"]
                            + downloaded_mod.dependencies["optional"]
                        )
                ):
                    break
            else:
                if dependency.downloaded:
                    dependency.remove()

        return 0

    @classmethod
    def search_mods(
            cls,
            query,
            version: str = "any",
            search_order: str = "downloaded"
    ):
        """Search mod portal (mods.factorio.com) for the mod

        Note:
            search_order known variants: ["downloaded", "updated"]

        Args:
            query (str): name of the mod to search
            version (str, optional): version of the mod to search
            search_order (str, optional): result sorting

        Returns:
            Generator[dict] | None: Dictionary of {"name", "description", "name_extended"}

        TODO:
            * optimize FOR cycle
        """

        return

        if search_order not in ["updated", "downloaded"]:
            return

        start_index = 1
        url = f"https://mods.factorio.com/{start_index}?"
        params = {
            "query": query,
            "version": version,
            "search_order": search_order
        }
        search_query = url + urlparse.urlencode(params)

        response = requests.get(search_query)
        if response.status_code != 200:
            logger.warning(
                f"""Could not download. Server is not responding. \
    Status code: {response.status_code}""")
            return

        soup = BeautifulSoup(response.text, "lxml")

        # filter <div class="mod-list"> block
        mod_list = soup.find('div', class_="mod-list")
        last_page_index = mod_list.find_previous_sibling(
        ).find_previous_sibling().find_all("a")[-2].text.strip()

        last_index = int(last_page_index) if last_page_index != "" else 1

        for page_index in range(start_index, last_index + 1):
            for block in mod_list.findChildren("div", recursive=False):
                link = block.find_all("a")[1]
                name = "/".join(link["href"].split("/")[2:])
                name_extended = link.text
                description = block.find("p", class_="pre-line").text.strip()
                yield {
                    "name": name,
                    "description": description,
                    "name_extended": name_extended
                }
            url = f"https://mods.factorio.com/{page_index + 1}?"
            search_query = url + urlparse.urlencode(params)
            response = requests.get(search_query)
            soup = BeautifulSoup(response.text, "lxml")
            mod_list = soup.find('div', class_="mod-list")

    @classmethod
    @property
    def downloaded_mods(cls) -> Generator:
        """Check for list of downloaded mods

        Returns:
            Generator[Mod]: Iterable through mods
        """

        return

        yield Mod("base")
        for filename in config.mods_file.parent.rglob("*.zip"):
            mod_name = filename.stem.rsplit("_", 1)[0]
            yield Mod(mod_name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"""<class '{__class__.__name__}' name: '{self.name}'>"""


class ModController:
    """Helper class to work with lots of mods"""

    def __init__(self):
        pass

    def remove(self, mod: Mod):
        """

        Args:
            mod:

        Returns:

        TODO:

        """

        pass

    def download(self, mod: Mod):
        """

        Args:
            mod:

        Returns:

        TODO:

        """

        pass

    def update(self, mod: Mod):
        """

        Args:
            mod:

        Returns:

        TODO:

        """

        pass

    def upgrade(self, mod: Mod):
        """

        Args:
            mod:

        Returns:

        TODO:

        """

        pass

    def search(self, query, version: str = "any", order: str = "downloaded"):
        """

        Args:
            query:
            version:
            order:

        Returns:

        TODO:

        """

        pass

    @classproperty
    def downloaded_list(cls):
        yield Mod("base")

        for filename in config.mods_file.rglob("*.zip"):
            yield Mod(filename.stem.rsplit("_", 1)[0])
