"""Global fixtures for ferroamp_operation_settings integration."""
# Fixtures allow you to replace functions with a Mock object. You can perform
# many options via the Mock to reflect a particular behavior from the original
# function that you want to see without going through the function's actual logic.
# Fixtures can either be passed into tests as parameters, or if autouse=True, they
# will automatically be used across all tests.
#
# Fixtures that are defined in conftest.py are available across all tests. You can also
# define fixtures within a particular test file to scope them locally.
#
# pytest_homeassistant_custom_component provides some fixtures that are provided by
# Home Assistant core. You can find those fixture definitions here:
# https://github.com/MatthewFlamm/pytest-homeassistant-custom-component/blob/master/pytest_homeassistant_custom_component/common.py
#
# See here for more info: https://docs.pytest.org/en/latest/fixture.html (note that
# pytest includes fixtures OOB which you can use as defined on this page)
from http.cookies import SimpleCookie
from unittest.mock import patch
import pytest


# pylint: disable=invalid-name
pytest_plugins = "pytest_homeassistant_custom_component"


# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
# pylint: disable=unused-argument
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enables loading of custom integration"""
    yield


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


# This fixture, when used, will result in calls to validate_input_sensors to return None. To have
# the call return a value, we would add the `return_value=<VALUE_TO_RETURN>` parameter to the
# patch call.
@pytest.fixture(name="bypass_validate_step_user")
def bypass_validate_step_user_fixture():
    """Skip calls to validate step user."""
    with patch(
        "custom_components.ferroamp_operation_settings.helpers.config_flow.FlowValidator.validate_step_user",
        return_value=None,
    ):
        yield


# This fixture is used to prevent HomeAssistant from doing Service Calls.
@pytest.fixture(name="skip_service_calls")
def skip_service_calls_fixture():
    """Skip service calls."""
    with patch("homeassistant.core.ServiceRegistry.async_call"):
        yield


# This fixture prevent Home Assistant to access internet.
@pytest.fixture(name="mock_api_wrapper_get_json", autouse=True)
def mock_api_wrapper_get_json_fixture():
    """Mock api_wrapper_get_json()."""

    response = {
        "_id": 1234,
        "emsConfig": {
            "data": {
                "battery": {
                    "powerRef": {"discharge": 0, "charge": 750},
                    "socRef": {"high": 100, "low": 15},
                },
                "pv": {"mode": 1},
                "grid": {
                    "limitExport": False,
                    "thresholds": {"high": 2000, "low": 1500},
                    "limitImport": False,
                    "ace": {"threshold": 9, "mode": 1},
                },
                "mode": 1,
            },
        },
    }

    with patch(
        "custom_components.ferroamp_operation_settings.helpers.api.ApiClientBase.api_wrapper_get_json",
        return_value=response,
    ):
        yield


class MockResponse:
    """Mock class for Response"""

    cookies: SimpleCookie[str] = SimpleCookie()


# This fixture prevent Home Assistant to access internet.
@pytest.fixture(name="mock_api_wrapper_post_json_cookies", autouse=True)
def mock_api_wrapper_post_json_cookies_fixture():
    """Mock api_wrapper_post_json_cookies()."""

    response: MockResponse = MockResponse()
    response.cookies["access_token"] = SimpleCookie()
    response.cookies["access_token"].set("access_token", "abcdef12345", "")

    with patch(
        "custom_components.ferroamp_operation_settings.helpers.api.ApiClientBase.api_wrapper_post_json_cookies",
        return_value=response.cookies,
    ):
        yield


# This fixture prevent Home Assistant to access internet.
@pytest.fixture(name="mock_api_wrapper_post_json_text", autouse=True)
def mock_api_wrapper_post_json_text_fixture():
    """Mock api_wrapper_post_json_text()."""

    with patch(
        "custom_components.ferroamp_operation_settings.helpers.api.ApiClientBase.api_wrapper_post_json_text",
        return_value="Created",
    ):
        yield
