from __future__ import annotations

import pathlib
from datetime import datetime
from typing import Literal

import requests


class FactorioAPI:
    base_url = "https://mods.factorio.com"

    @staticmethod
    def login(username: str, password: str) -> str:
        """Logs in to the Factorio authentication API using the provided username and password,
        and returns the authentication token as a string.

        Args:
            username (str): The username of the Factorio account.
            password (str): The password of the Factorio account.

        Returns:
            str: The authentication token as a string.

        Raises:
            requests.exceptions.RequestException: If there was an error with the request.
            APIError: If the API returned an error status code.

        """

        full_url = "https://auth.factorio.com/api-login"
        params = {
            "username": username,
            "password": password,
            "require_game_ownership": True
        }
        response = requests.post(full_url, params=params)

        if response.status_code == 200:
            return response.json()[0]
        else:
            # TODO: Handle other status code cases and raise appropriate exceptions
            response.raise_for_status()

    @classmethod
    def download(
            cls,
            download_url: str,
            username: str,
            token: str,
            filename: str | pathlib.Path,
            chunk_size: int = 8192,
            progress_callback=None,
            *args, **kwargs
    ) -> None:
        """
        Downloads a file from the specified URL using the provided authentication token and saves it to a file.
        The progress of the download can be monitored using a callback function.

        Args:
            download_url (str): The URL of the file to download.
            username (str): The username of the account.
            token (str): The authentication token of the account.
            filename (str | pathlib.Path): The local file path where the downloaded content will be saved.
            chunk_size (int, optional): The size of the download chunks in bytes. Defaults to 8192.
            progress_callback (callable, optional): A callback function to monitor the download progress. The
                function should accept a dictionary argument containing the following keys:
                - progress (float): The progress percentage of the download.
                - total (float): The maximum percentage. Default to 100.0.
                - downloaded_size (int): The size of downloaded file in bytes.
                - total_size (int): The size of downloading file in bytes.
                - rate (float): The download speed in bytes per second.
                Any additional keyword arguments specified by **kwargs can also be included in the dictionary.
            *args: Variable length argument list to pass to the progress_callback function.
            **kwargs: Arbitrary keyword arguments to pass to the progress_callback function. The following arguments
                are supported:

        Raises:
            requests.exceptions.RequestException: If there was an error with the request.
            APIError: If the API returned an error status code.

        """

        url = cls.base_url + download_url
        params = {
            "username": username,
            "token": token,
            "require_game_ownership": True
        }
        response = requests.get(url, params=params, stream=True)

        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            # Ensure the filename is a Path object
            filename = pathlib.Path(filename)

            # Add a temporary extension to the filename
            temp_filename = filename.with_suffix(f"{filename.suffix}.part")

            # Initialize variables for download speed calculation
            start_time = datetime.now()
            last_progress_time = start_time
            last_downloaded_size = 0

            kwargs["total_size"] = total_size
            kwargs["total"] = 100.0
            with open(temp_filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    downloaded_size += len(chunk)
                    file.write(chunk)

                    if progress_callback:
                        # Calculate progress percentage
                        progress = (downloaded_size / total_size) * 100

                        # Calculate download rate
                        current_time = datetime.now()
                        time_delta = (current_time - last_progress_time).total_seconds()
                        downloaded_delta = downloaded_size - last_downloaded_size
                        rate = downloaded_delta / time_delta if time_delta > 0 else 0

                        kwargs["progress"] = progress
                        kwargs["downloaded_size"] = downloaded_size
                        kwargs["rate"] = rate

                        progress_callback(*args, **kwargs)

                        last_progress_time = current_time
                        last_downloaded_size = downloaded_size

            # Rename the temporary file to the original filename once the download is complete
            temp_filename.rename(filename)

        else:
            # TODO: Handle other status code cases and raise appropriate exceptions
            response.raise_for_status()

    @classmethod
    def get_mods(
            cls,
            hide_deprecated: bool = True,
            page: int = 1,
            page_size: int | Literal["max"] = 25,
            sort: Literal[
                "name",
                "title",
                "owner",
                "summary",
                "downloads_count",
                "category",
                "score",
                "created_at",
                "updated_at"
            ] = "name",
            sort_order: Literal["asc", "desc"] = "desc",
            namelist: list[str] = None,
            version: Literal["0.13", "0.14", "0.15", "0.16", "0.17", "0.18", "1.0", "1.1"] = None
    ) -> dict:
        """Retrieves a list of mods from the Factorio mod portal using the HTTP GET method.

        Args:
            hide_deprecated (bool, optional): If True, deprecated mods will be filtered out. Defaults to True.
            page (int, optional): The page number to retrieve. Defaults to 1.
            page_size (int | Literal["max"], optional): The number of mods to retrieve per page. Defaults to 25.
            sort (Literal, optional): The field to sort the results by. Defaults to "name".
            sort_order (Literal, optional): The sort order, either "asc" (ascending) or "desc" (descending).
                Defaults to "desc".
            namelist (list[str], optional): A list of mod names to filter the results by.
            version (Literal, optional): The Factorio version to filter the results by.

        Returns:
            dict: The retrieved mods as a dictionary.

        Raises:
            requests.exceptions.RequestException: If there was an error with the HTTP request.
            APIError: If the API returned an error status code.

        Example usage:
            mods = get_mods(
                page=1,
                page_size=10,
                namelist=["YARM", "FNEI"],
                version="1.0"
            )

        """

        url = f"{cls.base_url}/api/mods"
        params = {
            "page_size": page_size,
            "page": page,
            "hide_deprecated": hide_deprecated,
            "namelist": ",".join(namelist) if namelist else None,
            "version": version,
            "sort": sort,
            "sort_order": sort_order
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            # TODO: Handle other status code cases and raise appropriate exceptions
            response.raise_for_status()

    @classmethod
    def get_mod_info(cls, mod_name: str) -> dict:
        """Retrieves information about a specific mod from the Factorio mod portal.

        Args:
            mod_name (str): The name of the mod to retrieve information for.

        Returns:
            dict: The retrieved mod information as a dictionary.

        Raises:
            requests.exceptions.RequestException: If there was an error with the request.
            APIError: If the API returned an error status code.

        """

        url = f"{cls.base_url}/api/mods/{mod_name}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            # TODO: Handle other status code cases and raise appropriate exceptions
            response.raise_for_status()
