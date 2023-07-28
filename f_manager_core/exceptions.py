class FileNotFoundException(Exception):
    def __init__(self, filename, *args):
        if args:
            super().__init__(
                f"""File {filename} is not found. Check your configuration settings for {', '.join(*args)} variables"""
            )
        else:
            super().__init__(
                f"""File {filename} is not found. Check your configuration settings."""
            )


class DefaultProfileRemoveError(Exception):
    def __init__(self):
        super().__init__("You are not allowed to remove default profile")


class UnknownSystem(Exception):
    pass


class GameNotFoundError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ModNotFoundError(Exception):
    def __init__(self, mod_name: str) -> None:
        super().__init__(f"Can't find '{mod_name}' mod in mods directory")


class BrokenModException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
