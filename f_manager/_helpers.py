from typing import Iterable


class classproperty(property):
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


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
        `min_version`, `max_version`, `from_min_version`, `to_max_version` and `version` may be missing
        if nobody gives a fuck which version of the mod

        MOD_CATEGORY: ["optional", "conflict", "parent", "require"]

        min_version: >=

        from_min_version: >

        max_version: <=

        to_max_version: <

        version: ==

    Returns:
        dict[str, str]: dependencies dictionary

    TODO:
        * what the fuck is that
        * make different docstring for Mod.dependencies or for that

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


def friendly_list(words: Iterable[str], joiner: str = "or", omit_empty: bool = True) -> str:
    """Generate a list of words as readable prose.

    >>> friendly_list(["foo", "bar", "baz"])
    "'foo', 'bar', or 'baz'"

    Note:
        Stolen from textual (https://github.com/Textualize/textual)

    Args:
        words: A list of words.
        joiner: The last joiner word. Defaults to "or".
        omit_empty: Should result containing None or not. (skip None)

    Returns:
        List as prose.

    """

    words = [
        repr(word) for word in sorted(words, key=str.lower) if word or not omit_empty
    ]
    if len(words) == 1:
        return words[0]
    elif len(words) == 2:
        word1, word2 = words
        return f"{word1} {joiner} {word2}"
    else:
        return f'{", ".join(words[:-1])}, {joiner} {words[-1]}'
