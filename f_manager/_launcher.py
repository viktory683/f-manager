import subprocess

from f_manager import config, exceptions
from f_manager._logger import logger
from f_manager._profile import Profile, TempProfile


class Save:
    """Implements game save

    TODO:
        * Write this shit
        * sync save with ``Profile``

    """

    pass


class Launcher:
    """A class to represent a game launcher"""

    def __init__(self, profile: Profile = None):
        """Initialize the launcher with the given profile

        Args:
            profile (Profile, optional): profile you want to load

        """

        self._temp_profile = TempProfile(profile)
        self.run()

    def run(self, save: Save = None):
        """Runs the game with given save

        Args:
            save (Save, optional): game save to load

        Returns:
            None

        TODO:
            * load save
            * test scenario where game relaunches (maybe game save mods synchronization) so can drop to default
                factorio `mod_list.json` file

        """

        if not isinstance(save, Save):
            raise TypeError("'save' entities should be of type 'Save'")

        if not config.game_folder.is_dir():
            raise exceptions.FileNotFoundException(config.game_folder)

        self._temp_profile.activate()

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

        self._temp_profile.deactivate()

        logger.info("Bye!")
