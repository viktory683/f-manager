class InvalidSearchOrder(Exception):
    pass


class APIcallError(Exception):
    def __init__(self, response):
        """
        Args:
            response (Response): response

        TODO:
            - check that response is not empty
            - different status codes messages

        """

        super().__init__(response.status_code)


class DependencyRemove(Exception):
    pass


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


class ProfileNotFoundError(Exception):
    def __init__(self, profile_name):
        super().__init__(f"Profile '{profile_name}' is not found")


class BaseModDisableError(Exception):
    def __init__(self):
        super().__init__("You are not allowed to disable base mod")


class BaseModRemoveError(Exception):
    def __init__(self):
        super().__init__("You are not allowed to remove base mod")


class DefaultProfileRemoveError(Exception):
    def __init__(self):
        super().__init__("You are not allowed to remove default profile")


class ModNotFoundError(Exception):
    def __init__(self, mod_name):
        super().__init__(f"'{mod_name}' was not found")


class ModExistsError(Exception):
    def __init__(self, mod_name):
        super().__init__(f"'{mod_name}' already exists")


class VersionNotFoundError(Exception):
    def __init__(self, mod_name, version):
        super().__init__(f"Not found version '{version}' of '{mod_name}' mod")
