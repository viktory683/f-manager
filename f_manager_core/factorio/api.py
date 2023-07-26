from pathlib import Path
from typing import List, Literal, Optional

import requests
from f_manager_core.factorio.const import LOGIN_BASE_URL, MOD_PORTAL_BASE_URL
from f_manager_core.factorio.exceptions import EmailAuthenticationRequired, LoginFailed

from f_manager_core.factorio.json_object_types import (
    BookmarkToggleStatus,
    Category,
    ModListResponse,
    Result,
)


def get_categories() -> List[Category]:
    """Retrieve a list of categories from the API.

    Raises:
        ValueError: If got an invalid category

    Returns:
        List[Category]: A list of categories, where each category is represented as a list of strings.
    """
    url = f"{MOD_PORTAL_BASE_URL}/api/categories"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    if not isinstance(data, list):
        raise ValueError("Could not parse category")

    return [Category(c) for c in data]


def get_mods(
    version: Literal["0.13", "0.14", "0.15", "0.16", "0.17", "0.18", "1.0", "1.1"],
    hide_deprecated: bool = True,
    page: int = 1,
    page_size: int | Literal["max"] = 25,
    sort: Literal["name", "created_at", "updated_at"] = "name",
    sort_order: Literal["asc", "desc"] = "desc",
    namelist: Optional[List[str]] = None,
) -> ModListResponse:
    """Retrieves a list of mods from the Factorio mod portal using the HTTP GET method.

    Args:
        version (Literal[`0.13`, `0.14`, `0.15`, `0.16`, `0.17`, `0.18`, `1.0`, `1.1`]): Only return non-deprecated mods compatible with this Factorio version
        hide_deprecated (bool, optional): Only return non-deprecated mods. Defaults to True.
        page (int, optional): Page number you would like to show. Makes it so you can see a certain part of the list without getting detail on all. Defaults to 1.
        page_size (int | Literal[`max`], optional): The amount of results to show in your search. Defaults to 25.
        sort (Literal[`name`, `created_at`, `updated_at`], optional): Sort results by this property. Defaults to name when not defined. Ignored for `page_size=max` queries. Defaults to "name".
        sort_order (Literal[`asc`, `desc`], optional): Sort results ascending or descending. Defaults to descending when not defined. Ignored for `page_size=max` queries. Defaults to "desc".
        namelist (Optional[List[str]], optional): Return only mods that match the given names. Response will include releases instead of latest_release. Defaults to None.

    Returns:
        ModListResponse
    """
    url = f"{MOD_PORTAL_BASE_URL}/api/mods"
    params = {
        "hide_deprecated": hide_deprecated,
        "page": page,
        "page_size": page_size,
        "sort": sort,
        "sort_order": sort_order,
        "namelist": namelist,
        "version": version,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    return ModListResponse(response.json())


def get_mods_short(mod_name: str) -> Result:
    """Return short information of a specific mod.

    Args:
        mod_name (str): The name of the mod to retrieve

    Returns:
        Result: Short information of a specific mod
    """
    url = f"{MOD_PORTAL_BASE_URL}/api/mods/{mod_name}"
    response = requests.get(url)
    response.raise_for_status()

    return Result(response.json())


def get_mods_full(mod_name: str) -> Result:
    """Returns more information of a mod.

    Args:
        mod_name (str): The name of the mod to retrieve

    Returns:
        Result: Full information of a specific mod
    """
    url = f"{MOD_PORTAL_BASE_URL}/api/mods/{mod_name}/full"
    response = requests.get(url)
    response.raise_for_status()

    return Result(response.json())


def post_token(
    username: str,
    password: str,
    api_version: Optional[str] = None,
    require_game_ownership: Optional[bool] = None,
    email_authentication_code: Optional[str] = None,
) -> str:
    """Factorio's Web Authentication API endpoint gives you a token in exchange for your username and password, which is used by several other Factorio web API endpoints.

    Args:
        username (str): Account username or e-mail.
        password (str): Account password.
        api_version (Optional[str], optional): (Technically) not required. API responses will be different than described. Defaults to None.
        require_game_ownership (Optional[bool], optional): If set to `True`, will fail authentication if the user account hasn't actually purchased Factorio.. Defaults to None.
        email_authentication_code (Optional[str], optional): If a previous login failed with `EmailAuthenticationRequired`, email authentication can be completed by including the code sent to the user via mail. Defaults to None.

    Raises:
        ValueError: If got an error but json isn't object
        ValueError: If got an error but no error provided
        LoginFailed: Wrong username or password
        EmailAuthenticationRequired: Need code from email

    Returns:
        str: Auth token is a hexadecimal encoded byte string
    """
    url = LOGIN_BASE_URL
    params = {
        "username": username,
        "password": password,
        "api_version": api_version,
        "require_game_ownership": require_game_ownership,
        "email_authentication_code": email_authentication_code,
    }
    response = requests.post(url, params=params)
    try:
        response.raise_for_status()
    except Exception as e:
        json_data = response.json()
        if not isinstance(json_data, dict):
            raise ValueError(f"Invalid JSON data: {json_data}") from e

        error = json_data.get("error")

        if not error:
            raise ValueError(f"Invalid JSON data: {json_data}") from e

        match error:
            case "login-failed":
                raise LoginFailed from e
            case "email-authentication-required":
                raise EmailAuthenticationRequired from e

    return response.json()[0]


def get_mod(username: str, token: str, download_url: str, filename: str | Path):
    """Downloads a file from the specified URL using the provided authentication token and saves it to a file.

    Args:
        username (str): The username of the account.
        token (str): The authentication token of the account.
        download_url (str): The URL of the file to download from `Release` objects.
        filename (str | Path): The local file path where the downloaded content will be saved.
    """
    url = f"https://mods.factorio.com{download_url}?username={username}&token={token}"
    response = requests.get(url, stream=True)
    response.raise_for_status()

    filename = Path(filename)
    with filename.open("wb") as file:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:
                file.write(chunk)


def get_bookmarks(username: str, token: str) -> List[str]:
    """Retrieve a list of bookmarks for a given user from the API.

    Args:
        username (str): The username of the user.
        token (str): The authentication token of the user.

    Raises:
        ValueError: If there was an error with the request.

    Returns:
        List[str]: A list of bookmarks as strings.
    """
    url = f"{MOD_PORTAL_BASE_URL}/api/bookmarks"
    params = {"username": username, "token": token}
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    if not isinstance(data, list):
        raise ValueError("Could not get bookmarks")

    return data


def post_bookmarks_toggle(
    username: str, token: str, mod: str, state: Literal["on", "off"]
) -> BookmarkToggleStatus:
    """Toggle the bookmark state of a specified mod for a given user using the API.

    Args:
        username (str): The username of the user.
        token (str): The authentication token of the user.
        mod (str): The mod identifier to toggle the bookmark state for.
        state (Literal[`on`, `off`]): The desired bookmark state.

    Returns:
        BookmarkToggleStatus
    """
    url = f"{MOD_PORTAL_BASE_URL}/api/bookmarks/toggle"
    params = {"username": username, "token": token, "mod": mod, "state": state}
    response = requests.post(url, params=params)
    response.raise_for_status()

    return BookmarkToggleStatus(response.json())
