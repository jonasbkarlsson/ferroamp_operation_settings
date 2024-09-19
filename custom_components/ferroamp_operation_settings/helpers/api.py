"""API Client."""

from copy import deepcopy
from json import dumps as json_dumps
import logging
import asyncio
import socket
import time
from typing import TypeVar
from urllib.parse import urldefrag, urlencode, urlparse, parse_qs
from uuid import uuid4
import aiohttp
import async_timeout
from oauthlib.oauth2 import WebApplicationClient
from pyquery import PyQuery as pq


_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}
TIMEOUT = 60

_T = TypeVar("_T")


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
        allow_redirects: bool = True,
    ) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                if method == "get_json":
                    response = await self._session.get(url, headers=headers)
                    _LOGGER.debug("response.status = %s", response.status)
                    return await response.json()

                elif method == "get":
                    response = await self._session.get(
                        url, headers=headers, allow_redirects=allow_redirects
                    )
                    _LOGGER.debug("response.status = %s", response.status)
                    return response

                elif method == "get_text":
                    response = await self._session.get(
                        url, headers=headers, allow_redirects=allow_redirects
                    )
                    _LOGGER.debug("response.status = %s", response.status)
                    return await response.text()

                elif method == "post_json_text":
                    response = await self._session.post(
                        url, headers=headers, json=json, allow_redirects=allow_redirects
                    )
                    _LOGGER.debug("response.status = %s", response.status)
                    return await response.text()

                elif method == "post_data":
                    response = await self._session.post(
                        url, headers=headers, data=data, allow_redirects=allow_redirects
                    )
                    _LOGGER.debug("response.status = %s", response.status)
                    return response

                elif method == "post_data_text":
                    response = await self._session.post(
                        url, headers=headers, data=data, allow_redirects=allow_redirects
                    )
                    _LOGGER.debug("response.status = %s", response.status)
                    return await response.text()

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
        allow_redirects: bool = True,
    ):
        """API wrapper for get_json"""
        return await self.api_wrapper(
            method="get_json",
            url=url,
            data=data,
            json=json,
            headers=headers,
            allow_redirects=allow_redirects,
        )

    async def api_wrapper_get_text(  # pylint: disable=dangerous-default-value
        self,
        url: str,
        data: dict = {},
        json: dict = {},
        headers: dict = {},
        allow_redirects: bool = True,
    ):
        """API wrapper for get_json"""
        return await self.api_wrapper(
            method="get_text",
            url=url,
            data=data,
            json=json,
            headers=headers,
            allow_redirects=allow_redirects,
        )

    async def api_wrapper_get(  # pylint: disable=dangerous-default-value
        self,
        url: str,
        data: dict = {},
        json: dict = {},
        headers: dict = {},
        allow_redirects: bool = True,
    ):
        """API wrapper for get_json"""
        return await self.api_wrapper(
            method="get",
            url=url,
            data=data,
            json=json,
            headers=headers,
            allow_redirects=allow_redirects,
        )

    async def api_wrapper_post_json_text(  # pylint: disable=dangerous-default-value
        self,
        url: str,
        data: dict = {},
        json: dict = {},
        headers: dict = {},
        allow_redirects: bool = True,
    ):
        """API wrapper for post_json_text"""
        return await self.api_wrapper(
            method="post_json_text",
            url=url,
            data=data,
            json=json,
            headers=headers,
            allow_redirects=allow_redirects,
        )

    async def api_wrapper_post_data_text(  # pylint: disable=dangerous-default-value
        self,
        url: str,
        data: dict = {},
        json: dict = {},
        headers: dict = {},
        allow_redirects: bool = True,
    ):
        """API wrapper for post_json_text"""
        return await self.api_wrapper(
            method="post_data_text",
            url=url,
            data=data,
            json=json,
            headers=headers,
            allow_redirects=allow_redirects,
        )

    async def api_wrapper_post_data(  # pylint: disable=dangerous-default-value
        self,
        url: str,
        data: dict = {},
        json: dict = {},
        headers: dict = {},
        allow_redirects: bool = True,
    ):
        """API wrapper for post_json_text"""
        return await self.api_wrapper(
            method="post_data",
            url=url,
            data=data,
            json=json,
            headers=headers,
            allow_redirects=allow_redirects,
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
        self.oauth2client = WebApplicationClient(
            "portal-first-gen", scope="openid", code_challenge_method="S256"
        )
        self._tokens = None
        self._access_token = None
        self._data = None

    async def get_new_tokens(self) -> None:
        """Get new access token and refresh token"""

        openid_baseurl = (
            "https://auth.eu.prod.ferroamp.com/realms/public/protocol/openid-connect"
        )
        portal_baseurl = "https://portal.ferroamp.com"

        nonce: str = str(uuid4())
        state: str = str(uuid4())
        session_state = None
        code = None
        authorization_code = None
        code_verifier = self.oauth2client.create_code_verifier(88)
        code_challenge = self.oauth2client.create_code_challenge(
            code_verifier, self.oauth2client.code_challenge_method
        )
        self.oauth2client.client_id = "portal-first-gen"

        ###### Get the login URL ################################################
        if self._session and self._session.cookie_jar:
            self._session.cookie_jar.clear()
        body = await self.api_wrapper_get_text(
            url=portal_baseurl, allow_redirects=False
        )
        _LOGGER.debug("get_new_tokens: After first GET.")
        d = pq(body)
        action = d("form").attr("action")

        if not action:
            redirect_uri = f"{portal_baseurl}/"
            self.oauth2client.client_id = "portal-frontend-ng-production"
            uri = self.oauth2client.prepare_request_uri(
                openid_baseurl + "/auth",
                redirect_uri=redirect_uri,
                state=state,
                code_challenge=code_challenge,
                code_challenge_method=self.oauth2client.code_challenge_method,
                response_mode="fragment",
                nonce=nonce,
            )
            headers = {}
            headers["Cookie"] = self.get_all_cookies()
            body = await self.api_wrapper_get_text(
                url=uri, headers=headers, allow_redirects=False
            )
            _LOGGER.debug("get_new_tokens: After first GET, attempt 2.")
            d = pq(body)
            action = d("form").attr("action")

        ##### Login the user #################################
        #
        ## Get "sesson_state" and "code"

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body_dict = {
            "username": f"{self._email}",
            "password": f"{self._password}",
        }
        body = urlencode(body_dict)
        headers["Cookie"] = self.get_all_cookies()
        _LOGGER.debug("get_new_tokens: Before first POST.")
        response = await self.api_wrapper_post_data(
            url=action, headers=headers, data=body
        )
        _LOGGER.debug("get_new_tokens: After first POST.")
        if response.status != 200:
            _LOGGER.error("Username and/or password is incorrect")
            _LOGGER.error("Failed to receive code")
            return None
        url = str(response.real_url)
        try:
            # Try using oauth2client.parse_request_uri_response()
            query_params = self.oauth2client.parse_request_uri_response(url)
            for key, value in query_params.items():
                if key == "session_state":
                    session_state = value
                if key == "code":
                    code = value
        except Exception:  # pylint: disable=broad-except
            # Try using urlparse()
            parsed_url = urlparse(url)
            if parsed_url.path == "/realms/public/login-actions/required-action":
                _LOGGER.error(
                    "Extra action needed. Please login using a web browser once."
                )
                return None
            fragment = parsed_url.fragment
            fragment_params = parse_qs(fragment)
            for key, value in fragment_params.items():
                if key == "session_state":
                    session_state = value[0]
                if key == "code":
                    code = value[0]

        if session_state is None or code is None:
            _LOGGER.error("Username and/or password is incorrect")
            _LOGGER.error("Failed to receive session_state and code")
            return None

        ##### Authorization Code Request ##################################
        #
        ## Get the "code" for authorization

        redirect_uri = f"{portal_baseurl}/app?session_state={session_state}&code={code}"
        self.oauth2client.client_id = "portal-frontend-ng-production"
        uri = self.oauth2client.prepare_request_uri(
            openid_baseurl + "/auth",
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=self.oauth2client.code_challenge_method,
            response_mode="fragment",
            nonce=nonce,
        )
        headers = {}
        headers["Cookie"] = self.get_all_cookies()
        _LOGGER.debug("get_new_tokens: Before second GET.")
        response = await self.api_wrapper_get(
            url=uri, headers=headers, allow_redirects=False
        )
        _LOGGER.debug("get_new_tokens: After second GET.")
        if response.status != 302:
            _LOGGER.error("Username and password are correct")
            _LOGGER.error("Failed to receive code")
            return None

        url = response.headers["Location"]
        parsed_url = urlparse(url)
        fragment = parsed_url.fragment
        fragment_params = parse_qs(fragment)

        if len(fragment_params) == 0:
            # Sometimes, the authorization code is not received on the first attempt.
            headers = {}
            headers["Cookie"] = self.get_all_cookies()
            uri = urldefrag(response.headers["Location"])[0]
            _LOGGER.debug("get_new_tokens: Before required action GET.")
            response = await self.api_wrapper_get(
                url=uri, headers=headers, allow_redirects=False
            )
            _LOGGER.debug("get_new_tokens: After required action GET.")
            if response.status != 302:
                _LOGGER.error("Username and password are correct")
                _LOGGER.error("Failed to receive code")
                return None

            url = response.headers["Location"]
            parsed_url = urlparse(url)
            fragment = parsed_url.fragment
            fragment_params = parse_qs(fragment)
            if len(fragment_params) == 0:
                _LOGGER.error("Username and password are correct")
                _LOGGER.error("Failed to receive authorization code")
                return None

        for key, value in fragment_params.items():
            if key == "code":
                authorization_code = value[0]

        if authorization_code is None:
            _LOGGER.error("Username and password are correct")
            _LOGGER.error("Failed to receive authorization code")
            return None

        headers = {}
        headers["Cookie"] = self.get_all_cookies()
        uri = urldefrag(response.headers["Location"])[0]
        _LOGGER.debug("get_new_tokens: Before third GET.")
        response = await self.api_wrapper_get(
            url=uri, headers=headers, allow_redirects=False
        )
        _LOGGER.debug("get_new_tokens: After third GET.")
        if response.status != 304 and response.status != 200:
            _LOGGER.error("Username and password are correct")
            _LOGGER.error("Failed to receive authorization code")
            return None

        ##### Access Token Request ###########################################
        #
        ## Get "access_token" and "refresh token", and their expiration times

        body = self.oauth2client.prepare_request_body(
            code=authorization_code,
            redirect_uri=redirect_uri,
            body="",
            include_client_id=True,
            code_verifier=code_verifier,
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        headers["Cookie"] = self.get_all_cookies()
        url = openid_baseurl + "/token"
        _LOGGER.debug("get_new_tokens: Before second POST.")
        response = await self.api_wrapper_post_data(url=url, headers=headers, data=body)
        _LOGGER.debug("get_new_tokens: After second POST.")
        if response.status != 200:
            _LOGGER.error("Username and password are correct")
            _LOGGER.error("Received authorization code")
            _LOGGER.error("Failed to receive tokens")
            return None

        json_data = await response.json()
        json_data["scope"] = "openid"
        try:
            tokens = self.oauth2client.parse_request_body_response(
                json_dumps(json_data), "openid"
            )
            self._tokens = tokens
            self._access_token = tokens["access_token"]
            _LOGGER.debug("get_new_tokens: New tokens received.")
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Username and password are correct")
            _LOGGER.error("Received authorization code")
            _LOGGER.error(
                "get_new_tokens: Could not read token information - %s", exception
            )

        return None

    def get_all_cookies(self) -> str:
        """Get all cookies from the cookie jar."""
        cookies = {}
        for cookie in self._session.cookie_jar:
            if cookie["domain"].endswith("ferroamp.com"):
                cookies[f"{cookie.key}"] = {
                    "key": f"{str(cookie.key)}",
                    "value": f"{str(cookie.value)}",
                }

        cookie_header = "; ".join(
            [
                f"{cookie_data['key']}={cookie_data['value']}"
                for cookie_data in cookies.values()
            ]
        )
        return cookie_header

    async def get_access_token(self) -> None:
        """Make sure we have a valid access token."""

        current_time = time.time()

        if self._access_token is None:
            # No Token
            await self.get_new_tokens()
            return self._access_token
        elif (
            self._access_token
            and self._tokens
            and self._tokens["expires_at"] - current_time < 30
        ):
            # Token is about to expire, so refresh it
            # pylint: disable=line-too-long
            openid_baseurl = "https://auth.eu.prod.ferroamp.com/realms/public/protocol/openid-connect"
            token_url = openid_baseurl + "/token"
            url, headers, body = self.oauth2client.prepare_refresh_token_request(
                token_url,
                refresh_token=self._tokens["refresh_token"],
                body="",
                scope=None,
                client_id="portal-frontend-ng-production",
            )
            _LOGGER.debug("get_access_token: Before first POST.")
            response = await self.api_wrapper_post_data(
                url=url, headers=headers, data=body
            )
            _LOGGER.debug("get_access_token: After first POST.")
            if response.status != 200:
                _LOGGER.debug("Failed to refresh token. Get new tokens instead.")
                self._access_token = None
                await self.get_new_tokens()
                return self._access_token

            json_data = await response.json()
            json_data["scope"] = "openid"
            try:
                tokens = self.oauth2client.parse_request_body_response(
                    json_dumps(json_data), "openid"
                )
                self._tokens = tokens
                self._access_token = tokens["access_token"]
                _LOGGER.debug("get_access_token: Tokens refreshed.")
            except Exception as exception:  # pylint: disable=broad-except
                _LOGGER.error(
                    "get_access_token: Could not read token information - %s", exception
                )
        else:
            # Token still valid
            _LOGGER.debug("get_access_token: Tokens still valid.")
        return self._access_token

    async def async_get_data(self) -> dict:
        """Get data from the API."""

        portal_baseurl = "https://portal.ferroamp.com"
        self._access_token = await self.get_access_token()
        if self._access_token is not None:
            url = (
                portal_baseurl
                + "/service/ems-config/v1/current/"
                + str(self._system_id)
            )
            headers = {"Authorization": "Bearer " + self._access_token}
            _LOGGER.debug("url = %s", url)
            data_ferroamp = await self.api_wrapper_get_json(url, headers=headers)
            self._data = deepcopy(data_ferroamp)
            _LOGGER.debug("After data_ferroamp = await self.api_wrapper")
            _LOGGER.debug("data_ferroamp = %s", data_ferroamp)
            return data_ferroamp

        return None

    async def async_set_data(self, body: dict) -> bool:
        """Set data to the API."""

        portal_baseurl = "https://portal.ferroamp.com"
        self._access_token = await self.get_access_token()
        if self._access_token is not None:
            url = (
                portal_baseurl
                + "/service/ems-config/v1/commands/set/"
                + str(self._system_id)
            )
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self._access_token,
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
