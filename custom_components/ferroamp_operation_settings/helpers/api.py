"""API Client."""
from copy import deepcopy
import logging
import asyncio
import socket
from typing import TypeVar
import aiohttp
import async_timeout

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}
TIMEOUT = 60

_T = TypeVar("_T")


class Cookie:
    """Cookie class"""

    @staticmethod
    def get_first_cookie(cookies):
        """Get the first cookie, if it exists."""
        if cookies is None or len(cookies) == 0:
            return None
        return cookies[next(iter(cookies))]


class ApiClientBase:
    """API client base class."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """API client base class."""
        self._session = session

    async def async_get_data(self) -> _T:
        """Get data from the API. This methid should be overloaded."""
        return None

    async def api_wrapper(  # pylint: disable=dangerous-default-value
        self,
        method: str,
        url: str,
        data: dict = {},
        json: dict = {},
        headers: dict = {},
    ) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                if method == "get_json":
                    response = await self._session.get(url, headers=headers)
                    return await response.json()

                elif method == "post_data_text":
                    response = await self._session.post(url, headers=headers, data=data)
                    return await response.text()

                elif method == "post_json_cookies":
                    response = await self._session.post(
                        url,
                        headers=headers,
                        json=json,
                        ssl=False,
                        allow_redirects=False,
                    )
                    if len(response.cookies) > 0:
                        print("Request was successful.")
                        # Access and print the cookies from the response
                        cookies = response.cookies
                        for key, value in cookies.items():
                            print(f"Cookie - {key}: {value.value}")
                        return response.cookies

                    print(f"Request failed with status code: {response.status}")
                    return None

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )
            raise exception

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
            raise exception

        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
            raise exception

        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
            raise exception


class FerroamoApiClient(ApiClientBase):
    """Ferroamp API client"""

    def __init__(
        self, system_id: int, email: str, password: str, session: aiohttp.ClientSession
    ) -> None:
        """Nordpool API Client."""
        super().__init__(session)
        self._system_id = system_id
        self._email = email
        self._password = password
        self._cookie = None
        self._data = None

    async def async_get_data(self) -> dict:
        """Get data from the API."""

        baseurl = "https://portal.ferroamp.com"
        if self._cookie is None:
            loginform = {
                "email": f"{self._email}",
                "password": f"{self._password}",
            }
            headers = {"Content-Type": "application/json"}
            url = baseurl + "/login"

            cookies = await self.api_wrapper(
                "post_json_cookies", url, json=loginform, headers=headers
            )
            if cookies is not None:
                self._cookie = Cookie.get_first_cookie(cookies)

        if self._cookie is not None:
            url = baseurl + "/service/ems-config/v1/current/" + str(self._system_id)
            headers = {"Cookie": f"{self._cookie.key}={self._cookie.value}"}
            _LOGGER.debug("url = %s", url)
            data_ferroamp = await self.api_wrapper("get_json", url, headers=headers)
            self._data = deepcopy(data_ferroamp)
            _LOGGER.debug("After data_ferroamp = await self.api_wrapper")

            _LOGGER.debug("data_ferroamp = %s", data_ferroamp)
            return data_ferroamp

        return None