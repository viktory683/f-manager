from f_manager.helpers import parse_version


class Version:
    """Represents a version

    Attributes:
        version (tuple): the version

    """

    def __init__(self, version: str | tuple):
        """Constructs a Version object

        Args:
            version_str (str): the version string

        """

        if not isinstance(version, (tuple, str)):
            raise TypeError("Version must be a tuple or a string")

        if isinstance(version, str):
            version = parse_version(version)

        self.version = version

    def __ge__(self, other):
        if not isinstance(other, (tuple, Version)):
            raise TypeError("The operand on the right must be of type tuple or Version")

        if isinstance(other, Version):
            other_version = other.version
        elif all(map(lambda v: isinstance(v, int), other)):
            other_version = other
        else:
            raise TypeError("The operand of type tuple has to be tuple[int]")

        # alignment by length
        self_version = list(self.version)
        other_version = list(other_version)
        if len(self_version) > len(other_version):
            other_version.extend(0 for _ in range(len(self_version) - len(other_version)))
        elif len(self_version) < len(other_version):
            self_version.extend(0 for _ in range(len(other_version) - len(self_version)))

        flag = False

        for sv, ov in zip(reversed(self_version), reversed(other_version)):
            flag = sv >= ov

        return flag

    def __le__(self, other):
        if not isinstance(other, (tuple, Version)):
            raise TypeError(
                "The operand on the right must be of type tuple or Version")

        if isinstance(other, Version):
            other_version = other.version
        elif all(map(lambda v: isinstance(v, int), other)):
            other_version = other
        else:
            raise TypeError("The operand of type tuple has to be tuple[int]")

        # alignment by length
        self_version = list(self.version)
        other_version = list(other_version)
        if len(self_version) > len(other_version):
            other_version.extend(0 for _ in range(len(self_version) - len(other_version)))
        elif len(self_version) < len(other_version):
            self_version.extend(0 for _ in range(len(other_version) - len(self_version)))

        flag = False

        for sv, ov in zip(reversed(self_version), reversed(other_version)):
            flag = sv <= ov

        return flag

    def __gt__(self, other):
        if not isinstance(other, (tuple, Version)):
            raise TypeError(
                "The operand on the right must be of type tuple or Version")

        if isinstance(other, Version):
            other_version = other.version
        elif all(map(lambda v: isinstance(v, int), other)):
            other_version = other
        else:
            raise TypeError("The operand of type tuple has to be tuple[int]")

        # alignment by length
        self_version = list(self.version)
        other_version = list(other_version)
        if len(self_version) > len(other_version):
            other_version.extend(0 for _ in range(len(self_version) - len(other_version)))
        elif len(self_version) < len(other_version):
            self_version.extend(0 for _ in range(len(other_version) - len(self_version)))

        flag = False

        for sv, ov in zip(reversed(self_version), reversed(other_version)):
            flag = sv > ov

        return flag

    def __lt__(self, other):
        if not isinstance(other, (tuple, Version)):
            raise TypeError(
                "The operand on the right must be of type tuple or Version")

        if isinstance(other, Version):
            other_version = other.version
        elif all(map(lambda v: isinstance(v, int), other)):
            other_version = other
        else:
            raise TypeError("The operand of type tuple has to be tuple[int]")

        # alignment by length
        self_version = list(self.version)
        other_version = list(other_version)
        if len(self_version) > len(other_version):
            other_version.extend(0 for _ in range(len(self_version) - len(other_version)))
        elif len(self_version) < len(other_version):
            self_version.extend(0 for _ in range(len(other_version) - len(self_version)))

        flag = False

        for sv, ov in zip(reversed(self_version), reversed(other_version)):
            flag = sv < ov

        return flag

    def __ne__(self, other):
        if not isinstance(other, (tuple, Version)):
            raise TypeError(
                "The operand on the right must be of type tuple or Version")

        if isinstance(other, Version):
            other_version = other.version
        elif all(map(lambda v: isinstance(v, int), other)):
            other_version = other
        else:
            raise TypeError("The operand of type tuple has to be tuple[int]")

        return self.version != other_version

    def __eq__(self, other):
        if not isinstance(other, (tuple, Version)):
            raise TypeError(
                "The operand on the right must be of type tuple or Version")

        if isinstance(other, Version):
            other_version = other.version
        elif all(map(lambda v: isinstance(v, int), other)):
            other_version = other
        else:
            raise TypeError("The operand of type tuple has to be tuple[int]")

        return self.version == other_version

    def __str__(self) -> str:
        return ".".join(self.version)

    def __repr__(self) -> str:
        return f"<class '{__class__.__name__}' version: '{self.version}'>"
