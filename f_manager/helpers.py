from typing import Any


class classproperty(property):
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


def parse_version(version_raw: str) -> tuple[int]:
    """

    Args:
        version_raw (str): raw version string like `1.2.3`

    Returns:
        tuple[int]: list of version pieces like ``(1, 2, 3)``
    """

    version = []

    piece = ""
    for ch in version_raw:
        if ch.isdigit():
            piece += ch
        else:
            version.append(int(piece))
            piece = ""

    version.append(int(piece))

    return tuple(version)


def parse_dependency(dep_raw: str) -> dict[str, str]:
    """Parses raw dependency string

    Args:
        dep_raw (str): raw dependency string

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
        dict[str, str]: dependencies dictionary
"""

    dep = {}

    categories = {
        "optional": ["?", "(?)"],
        "conflict": ["!", "(!)"],
        "parent": ["~", "(~)"],
        # "require": None
    }

    comparisons = {
        "min_version": ">=",
        "max_version": "<=",
        # "version": "==",
        "from_min_version": ">",
        "to_max_version": "<"
    }

    for category, prefixes in categories.items():
        if any(map(lambda pref: dep_raw.startswith(pref), prefixes)):
            dep["category"] = category

            for prefix in prefixes:
                if dep_raw.startswith(prefix):
                    dep_raw = dep_raw.replace(prefix, "")
                    break

            break
    else:
        dep["category"] = "require"

    for value in comparisons.values():
        if value in dep_raw:
            args = dep_raw.split(value)
            matches = [args[0].strip()]
            for arg in args[1:]:
                matches.append(value)
                matches.append(arg.strip())
            break
    else:
        matches = [dep_raw.strip()]

    match matches:
        case [name, comparison, version]:
            dep["name"] = name
            dep[
                {
                    value: key
                    for key, value
                    in comparisons.items()
                }[comparison]
            ] = version
        case [name]:
            dep["name"] = name

    return dep
