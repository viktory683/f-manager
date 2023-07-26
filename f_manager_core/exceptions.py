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
