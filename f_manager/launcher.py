import subprocess

from . import config, exceptions
from .logger import logger
from .mods_profile import Profile, TempProfile

# TODO sync save with profile


class Save:
    # implements game save
    pass


class Launcher:
    def __init__(self, profile: Profile = None):
        self.temp_profile = TempProfile(profile)
        self.run()

    def run(self, save: Save = None):
        # TODO load save

        # TODO test scenario where game relaunches\
        # TODO (game save mods synchronization)

        # TODO can drop to default factorio mod_list.json file

        if not config.game_folder.is_dir():
            raise exceptions.FileNotFoundException(config.game_folder)

        self.temp_profile.activate()

        game_path = (
            config.game_folder
            .joinpath("bin")
            .joinpath("x64")
            .joinpath("factorio")
        )
        mods_path = config.mods_file.parent

        logger.info("Starting game")

        subprocess.Popen(
            f"{game_path} --mod-directory {mods_path}", shell=True
        )

        self.temp_profile.deactivate()

        logger.info("Bye!")
