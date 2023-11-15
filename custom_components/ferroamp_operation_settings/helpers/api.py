"""API Client."""
from copy import deepcopy
from datetime import datetime, timedelta
from http.cookies import Morsel, SimpleCookie
import logging
import asyncio
import socket
from typing import TypeVar
from urllib.parse import urlencode
import aiohttp
import async_timeout
from pyquery import PyQuery as pq

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}
TIMEOUT = 60

_T = TypeVar("_T")


class Cookie:
    """Cookie class"""

    @staticmethod
    def get_first_cookie(cookies: SimpleCookie):
        """Get the first cookie, if it exists."""
        if cookies is None or len(cookies) == 0:
            return None
        return cookies[next(iter(cookies))]

    @staticmethod
    def get_expires(cookie: Morsel) -> datetime:
        """Get the expire time for the cookie."""
        date_string = cookie["expires"]
        date_format = "%a, %d %b %Y %H:%M:%S %Z"
        parsed_datetime: datetime.datetime = datetime.strptime(date_string, date_format)
        return parsed_datetime


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
                    _LOGGER.debug("response.status = %s", response.status)
                    return await response.json()

                elif method == "get_text":
                    response = await self._session.get(url, headers=headers)
                    _LOGGER.debug("response.status = %s", response.status)
                    return await response.text()

                elif method == "post_json_text":
                    response = await self._session.post(url, headers=headers, json=json)
                    _LOGGER.debug("response.status = %s", response.status)
                    return await response.text()

                elif method == "post_data_text":
                    response = await self._session.post(url, headers=headers, data=data)
                    _LOGGER.debug("response.status = %s", response.status)
                    return await response.text()

                elif method == "post_json_cookies":
                    response = await self._session.post(
                        url,
                        headers=headers,
                        json=json,
                        #                        ssl=False,
                        allow_redirects=False,
                    )
                    _LOGGER.debug("response.status = %s", response.status)

                    # Check if a cookie was returned
                    if len(response.cookies) > 0:
                        _LOGGER.debug("Cookies received.")
                        # Access and print the cookies from the response
                        # cookies = response.cookies
                        # for key, value in cookies.items():
                        #    print(f"Cookie - {key}: {value.value}")
                        return Cookie.get_first_cookie(response.cookies)

                    # Check in the cookie_jar
                    for cookie in self._session.cookie_jar:
                        if cookie.key == "access_token":
                            _LOGGER.debug("Cookies received.")
                            return cookie

                    _LOGGER.debug(
                        "Cookies NOT received. Status code = %s", response.status
                    )
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

    async def api_wrapper_get_json(  # pylint: disable=dangerous-default-value
        self,
        url: str,
        data: dict = {},
        json: dict = {},
        headers: dict = {},
    ):
        """API wrapper for get_json"""
        return await self.api_wrapper(
            method="get_json", url=url, data=data, json=json, headers=headers
        )

    async def api_wrapper_get_text(  # pylint: disable=dangerous-default-value
        self,
        url: str,
        data: dict = {},
        json: dict = {},
        headers: dict = {},
    ):
        """API wrapper for get_json"""
        return await self.api_wrapper(
            method="get_text", url=url, data=data, json=json, headers=headers
        )

    async def api_wrapper_post_json_text(  # pylint: disable=dangerous-default-value
        self,
        url: str,
        data: dict = {},
        json: dict = {},
        headers: dict = {},
    ):
        """API wrapper for post_json_text"""
        return await self.api_wrapper(
            method="post_json_text", url=url, data=data, json=json, headers=headers
        )

    async def api_wrapper_post_data_text(  # pylint: disable=dangerous-default-value
        self,
        url: str,
        data: dict = {},
        json: dict = {},
        headers: dict = {},
    ):
        """API wrapper for post_json_text"""
        return await self.api_wrapper(
            method="post_data_text", url=url, data=data, json=json, headers=headers
        )

    async def api_wrapper_post_json_cookies(  # pylint: disable=dangerous-default-value
        self,
        url: str,
        data: dict = {},
        json: dict = {},
        headers: dict = {},
    ):
        """API wrapper for post_json_cookies"""
        return await self.api_wrapper(
            method="post_json_cookies", url=url, data=data, json=json, headers=headers
        )


class FerroampApiClient(ApiClientBase):
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

    def check_cookie_expires(self):
        """Check if the cookie is about to expire"""
        if self._cookie is not None:
            _LOGGER.debug("Cookie expires = %s", Cookie.get_expires(self._cookie))
            expires = Cookie.get_expires(self._cookie)  # Assumes time is UTC
            now = datetime.utcnow()
            delta = expires - now
            margin = timedelta(seconds=60)
            if delta < margin:
                _LOGGER.debug("Cookie expires soon.")
                self._cookie = None

    def get_all_cookies(self) -> {}:
        """Get all cookies from the cookie jar."""
        cookies = {}
        for cookie in self._session.cookie_jar:
            if cookie["domain"].endswith("ferroamp.com"):
                cookies[f"{cookie.key}"] = {
                    "key": f"{cookie.key}",
                    "value": f"{cookie.value}",
                }
        return cookies

    def get_cookie_from_jar(self, key: str) -> Morsel | None:
        """Get one cookie from the cookie jar."""
        for cookie in self._session.cookie_jar:
            if cookie["domain"].endswith("ferroamp.com"):
                if cookie.key == key:
                    return cookie
        return None

    async def get_cookie_from_login(self, baseurl: str):
        """Get cookies"""

        cookie = None
        try:
            _LOGGER.debug("get_cookie_from_login: Before GET.")
            body = await self.api_wrapper_get_text(url=baseurl)
            _LOGGER.debug("get_cookie_from_login: After GET.")

            d = pq(body)
            action = d("form").attr("action")
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            body_dict = {
                "username": f"{self._email}",
                "password": f"{self._password}",
            }
            body = urlencode(body_dict)
            headers["Cookie"] = self.get_all_cookies()
            _LOGGER.debug("get_cookie_from_login: Before first POST.")
            response = await self.api_wrapper_post_data_text(
                url=action, headers=headers, data=body
            )
            _LOGGER.debug("get_cookie_from_login: After first POST.")

            d = pq(response)
            action = d("form").attr("action")
            input_all = d("form").find("input")
            body_dict = {}
            for input_one in input_all:
                body_dict[input_one.name] = input_one.value
            body = urlencode(body_dict)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            headers["Cookie"] = self.get_all_cookies()

            _LOGGER.debug("get_cookie_from_login: Before second POST.")
            response = await self.api_wrapper_post_data_text(
                url=action, headers=headers, data=body
            )
            _LOGGER.debug("get_cookie_from_login: After second POST.")

            cookie = self.get_cookie_from_jar("access_token")
            if cookie:
                _LOGGER.debug("get_cookie_from_login: Cookie found.")
            else:
                _LOGGER.debug("get_cookie_from_login: No cookie found.")

        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.debug(
                "get_cookie_from_login: Something wrong happened! - %s", exception
            )

        return cookie

    async def get_cookie(self, baseurl: str):
        """Make sure we have a valid cookie."""

        self.check_cookie_expires()
        if self._cookie is None:
            cookie = await self.get_cookie_from_login(baseurl)
            if cookie is not None:
                self._cookie = cookie
            else:
                loginform = {
                    "email": f"{self._email}",
                    "password": f"{self._password}",
                }
                headers = {"Content-Type": "application/json"}
                url = baseurl + "/login"
                cookie = await self.api_wrapper_post_json_cookies(
                    url, json=loginform, headers=headers
                )
                if cookie is not None:
                    self._cookie = cookie

    async def async_get_data(self) -> dict:
        """Get data from the API."""

        baseurl = "https://portal.ferroamp.com"
        await self.get_cookie(baseurl)
        if self._cookie is not None:
            url = baseurl + "/service/ems-config/v1/current/" + str(self._system_id)
            headers = {"Cookie": f"{self._cookie.key}={self._cookie.value}"}
            _LOGGER.debug("url = %s", url)
            data_ferroamp = await self.api_wrapper_get_json(url, headers=headers)
            self._data = deepcopy(data_ferroamp)
            _LOGGER.debug("After data_ferroamp = await self.api_wrapper")
            _LOGGER.debug("data_ferroamp = %s", data_ferroamp)
            return data_ferroamp

        return None

    async def async_set_data(self, body: dict) -> bool:
        """Set data to the API."""

        baseurl = "https://portal.ferroamp.com"
        await self.get_cookie(baseurl)
        if self._cookie is not None:
            url = (
                baseurl + "/service/ems-config/v1/commands/set/" + str(self._system_id)
            )
            headers = {
                "Content-Type": "application/json",
                "Cookie": f"{self._cookie.key}={self._cookie.value}",
            }
            _LOGGER.debug("url = %s", url)
            _LOGGER.debug("headers = %s", headers)
            response = await self.api_wrapper_post_json_text(
                url, headers=headers, json=body
            )
            _LOGGER.debug("response = %s", response)

            if response == "Created":
                # Configuration successfully updated!
                return True

        return False
