import json
import shutil

from . import config, exceptions
from .logger import logger
from .mod import Mod


class Profile:
    # TODO docstring
    def __init__(self, name="default", save_dir=None):
        self.name = name
        self.name_bak = None
        self.new_name = None
        self._mods: list[Mod] = None

        self.save_dir = save_dir or config.profiles_dir

    @property
    def mods(self) -> list[Mod]:
        if self._mods:
            return self._mods

        if self.exists():
            with self.save_dir.joinpath(f"{self.name}.json").open() as f:
                mod_list = json.load(f)["mods"]

            self._mods = [
                Mod(mod.get("name"), mod.get("enabled"))
                for mod in mod_list
            ]
        elif self.name != "default":
            self._mods = [Mod("base", True)]
        else:
            if not config.mods_file.exists():
                raise exceptions.FileNotFoundException(config.mods_file)

            with config.mods_file.open() as f:
                mod_list = json.load(f)["mods"]

            self._mods = [
                Mod(mod.get("name"), mod.get("enabled"))
                for mod in mod_list
            ]

        return self._mods

    def save(self):
        mod_list = {"mods": []}
        for mod in self.mods:
            mod_list["mods"].append({"name": mod.name, "enabled": mod.enabled})

        if self.new_name:
            if self.exists():
                self.save_dir.joinpath(f"{self.name}.json").unlink()
            self.name = self.new_name

        if not self.save_dir.is_dir():
            logger.warning("Profiles directory not found. Creating new")
        self.save_dir.mkdir(parents=True, exist_ok=True)

        with self.save_dir.joinpath(f"{self.name}.json").open("w") as f:
            json.dump(mod_list, f, ensure_ascii=False, indent=4)

        logger.info(f"[{self.name}] saved to \
{self.save_dir.joinpath(f'{self.name}.json')}")

    def set_mods(self, mods: list[Mod]):
        self._mods = mods

        logger.info(f"[{self.name}] updated with mods: \
[{' '.join(map(lambda mod: mod.name, mods))}]")

    def rename(self, new_name):
        self.new_name = new_name

        logger.info(f"[{self.name}] renamed to: {self.new_name}\n\
New name will be changed on save")

    def exists(self):
        return self.save_dir.joinpath(f"{self.name}.json").is_file()

    def delete(self):
        if not self.exists():
            logger.warning(f"[{self.name}] does not exist. Skipping delete")
            return

        if self.name == "default":
            raise exceptions.DefaultProfileRemoveError()

        self.save_dir.joinpath(f"{self.name}.json").unlink()

        logger.info(f"[{self.name}] deleted.")

    def enable(self, mod: Mod):
        for i, profile_mod in enumerate(self.mods):
            if profile_mod.name == mod.name:
                if self._mods[i].enabled:
                    logger.warning(f"[{self.name}] already have enabled \
'{mod.name}' mod. Skipping")
                    return

                self._toggle_mod_by_id(i, True)
                return

        logger.warning(f"[{self.name}] does not have added '{mod.name}'")

    def disable(self, mod: Mod):
        for i, profile_mod in enumerate(self.mods):
            if profile_mod.name == mod.name:
                if not self._mods[i].enabled:
                    logger.warning(f"[{self.name}] already have disabled \
'{mod.name}' mod. Skipping")
                    return

                self._toggle_mod_by_id(i, False)
                return

        logger.warning(f"[{self.name}] does not have added '{mod.name}'")

    def _toggle_mod_by_id(self, id, state):
        self._mods[id].enabled = state

        logger.info(f"[{self.name}] {'enabled' if state else 'disabled'} \
'{self._mods[id].name}' mod")

    def add(self, mod: Mod):
        for profile_mod in self.mods:
            if profile_mod.name == mod.name:
                logger.warning(f"[{self.name}] already added '{mod.name}' mod")

                return

        self._mods = (self.mods + []) + [Mod(mod.name, True)]

        logger.info(f"[{self.name}] updated with '{mod.name}' mod \
(enabled by default)")

    def remove(self, mod: Mod):
        for i, profile_mod in enumerate(self.mods):
            if profile_mod.name == mod.name:
                self._mods = self.mods[:i] + self.mods[i + 1:]

                logger.info(f"[{self.name}] removed '{mod.name}' mod")

                return

        logger.warning(f"[{self.name}] does't have '{mod.name}' mod in list]")

    @classmethod
    def enable_for_all(cls, mod: Mod, profiles=None):
        # profiles: list[NewProfile]
        cls._toggle_for_all(mod, True, profiles)

    @classmethod
    def disable_for_all(cls, mod: Mod, profiles=None):
        # profiles: list[NewProfile]
        cls._toggle_for_all(mod, False, profiles)

    @classmethod
    def _toggle_for_all(cls, mod: Mod, state, profiles=None):
        # profiles: list[NewProfile]
        if profiles is None:
            profiles = cls.list_profiles()

        for profile in profiles:
            if state:
                profile.enable(mod)
            else:
                profile.disable(mod)
            profile.save()

    @classmethod
    def add_for_all(cls, mod: Mod, profiles=None):
        if profiles is None:
            profiles = cls.list_profiles()

        for profile in profiles:
            profile.add(mod)
            profile.save()

    @classmethod
    def remove_for_all(cls, mod: Mod, profiles=None):
        if profiles is None:
            profiles = cls.list_profiles()

        for profile in profiles:
            profile.remove(mod)
            profile.save()

    @classmethod
    def list_profiles(cls):
        if not config.profiles_dir.is_dir():
            logger.warning("Profiles directory is not found")
            return

        for filename in config.profiles_dir.rglob("*.json"):
            yield Profile(filename.stem)


class TempProfile(Profile):
    def __init__(self, profile: Profile = None):
        super().__init__("default" if profile is None else profile.name)

    def activate(self):
        if not self.exists():
            self.save()

        if not config.mods_file.is_file():
            raise exceptions.FileNotFoundException(config.mods_file)

        downloaded_mods = Mod.downloaded_mods
        profile_mods = self.mods

        mod_list = []

        for mod in profile_mods:
            if mod.downloaded:
                mod_list.append({"name": mod.name, "enabled": mod.enabled})
            elif mod.enabled:
                raise exceptions.ModNotFoundError(mod.name)

        simple_profile_mods = map(
            lambda mod: mod.name,
            filter(
                lambda mod: mod.downloaded,
                profile_mods
            )
        )

        mod_list.extend(
            {"name": mod.name, "enabled": False}
            for mod in downloaded_mods
            if mod.name not in simple_profile_mods
        )

        shutil.copy(
            config.mods_file,
            config.mods_file.parent.joinpath("mod-list.json.bak")
        )

        with config.mods_file.open("w") as f:
            json.dump({"mods": mod_list}, f, indent=4, ensure_ascii=False)

        logger.info(f"[{self.name}] extended and filtered was saved to \
{config.mods_file}.\nOld mod-list.json was saved to \
{config.mods_file.parent.joinpath('mod-list.json.bak')}")
        # shutil.copy(
        #     self.save_dir.joinpath(f"{self.name}.json"),
        #     config.mods_file
        # )

    def deactivate(self):
        if not config.mods_file.parent.joinpath("mod-list.json.bak").is_file():
            raise exceptions.FileNotFoundException(
                config.mods_file.parent.joinpath("mod-list.json.bak")
            )

        shutil.copy(
            config.mods_file.parent.joinpath("mod-list.json.bak"),
            config.mods_file
        )

        logger.info("Original mod-list.json was restored")
