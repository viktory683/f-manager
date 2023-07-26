import os
import pathlib
from typing import Any, Dict, List, Optional, Tuple

from packaging.requirements import Requirement, InvalidRequirement
from packaging.specifiers import SpecifierSet


def parse_dependencies(
    dependencies: List[str],
) -> Tuple[
    List[Tuple[str, SpecifierSet]],
    List[Tuple[str, SpecifierSet]],
    List[Tuple[str, SpecifierSet]],
    List[Tuple[str, SpecifierSet]],
    List[Tuple[str, SpecifierSet]],
]:
    """
    Parse dependencies from a Factorio mod's info.json file.

    Args:
        dependencies (List[str]): A list of dependency strings extracted from the info.json file.

    Returns:
        Tuple: A tuple containing five lists:

            - `mandatory_dependencies`: List of tuples with package name and version specifier for hard requirements.
            - `optional_dependencies`: List of tuples with package name and version specifier for optional dependencies.
            - `hidden_optional_dependencies`: List of tuples with package name and version specifier for hidden optional dependencies.
            - `no_load_order_dependencies`: List of tuples with package name and version specifier for dependencies that do not affect load order.
            - `incompatible_dependencies`: List of tuples with package name and version specifier for incompatible dependencies.

    """  # noqa: E501

    def parse_dependency_string(dependency: str) -> Tuple[str, SpecifierSet]:
        try:
            req = Requirement(dependency)
            return req.name, req.specifier
        except InvalidRequirement:
            # print("Found fucking space!")
            # print(e)
            dependency = dependency.replace(" ", "_", 1)
            name, specifier = parse_dependency_string(dependency)
            name = name.replace("_", " ", 1)
            return name, specifier

    mandatory_dependencies = []
    optional_dependencies = []
    hidden_optional_dependencies = []
    no_load_order_dependencies = []
    incompatible_dependencies = []

    for dependency in dependencies:
        if dependency.startswith("?"):
            name, specifier = parse_dependency_string(dependency[1:].strip())
            optional_dependencies.append((name, specifier))
        elif dependency.startswith("(?)"):
            name, specifier = parse_dependency_string(dependency[3:].strip())
            hidden_optional_dependencies.append((name, specifier))
        elif dependency.startswith("~"):
            name, specifier = parse_dependency_string(dependency[1:].strip())
            no_load_order_dependencies.append((name, specifier))
        elif dependency.startswith("!"):
            name, specifier = parse_dependency_string(dependency[1:].strip())
            incompatible_dependencies.append((name, specifier))
        else:
            name, specifier = parse_dependency_string(dependency.strip())
            mandatory_dependencies.append((name, specifier))

    return (
        mandatory_dependencies,
        optional_dependencies,
        hidden_optional_dependencies,
        no_load_order_dependencies,
        incompatible_dependencies,
    )


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


def expand_path(path) -> pathlib.Path:
    # Expand environment variables
    path = os.path.expandvars(path)

    # Expand user home directory
    path = os.path.expanduser(path)

    # Normalize the path (removes double dots, etc.)
    path = os.path.normpath(path)

    return pathlib.Path(path)


def sort_query(
    query: str,
    search_terms: List[Dict[str, Any]],
    cutoff: float = 0.002,
    weights: Optional[Tuple[float, float, float]] = None,
) -> List[Dict[str, Any]]:
    """Sort search terms based on their similarity to a given query.

    The function computes the weighted similarity between the query and each item in the search_terms list. Items with a similarity score above the specified cutoff value are filtered and sorted in descending order of similarity.

    Args:
        query (str): The user query as a string.
        search_terms (List[Dict[str, Any]]): A list of dictionaries containing search terms, with keys such as "name", "title", and "summary".
        cutoff (float, optional): A float representing the similarity score cutoff value. Default is 0.002.
        weights (Optional[Tuple[float, float, float]], optional): An optional tuple of floats representing the weights for "name", "title", and "summary". Default is (0.5, 0.3, 0.2).

    Returns:
        List[Dict[str, Any]]: A list of filtered and sorted search terms based on their similarity to the query.

    """  # noqa: E501

    import nltk
    from nltk.tokenize import word_tokenize

    # Check if 'punkt' is already downloaded
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")

    if not weights:
        weights = (0.5, 0.3, 0.2)

    name_weight, title_weight, summary_weight = weights

    def token_similarity(a, b):
        tokens_a = set(word_tokenize(a.lower()))
        tokens_b = set(word_tokenize(b.lower()))
        return len(tokens_a.intersection(tokens_b)) / len(tokens_a.union(tokens_b))

    def weighted_similarity(q, item):
        name_similarity = token_similarity(q, item["name"]) if "name" in item else 0
        title_similarity = token_similarity(q, item["title"]) if "title" in item else 0
        summary_similarity = (
            token_similarity(q, item["summary"]) if "summary" in item else 0
        )

        return (
            name_weight * name_similarity
            + title_weight * title_similarity
            + summary_weight * summary_similarity
        )

    for item in search_terms:
        item["similarity"] = weighted_similarity(query, item)

    filtered_search_terms = sorted(
        [item for item in search_terms if item["similarity"] >= cutoff],
        key=lambda x: x["similarity"],
        reverse=True,
    )

    return filtered_search_terms
