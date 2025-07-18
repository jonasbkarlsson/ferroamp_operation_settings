"""Test ferroamp_operation_settings config flow."""
from typing import Any, Dict
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ferroamp_operation_settings.const import DOMAIN

from .const import (
    MOCK_CONFIG_ALL,
    MOCK_OPTIONS_ALL,
)


# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with patch(
        #     "custom_components.ferroamp_operation_settings.async_setup",
        #     return_value=True,
        # ), patch(
        "custom_components.ferroamp_operation_settings.async_setup_entry",
        return_value=True,
    ):
        yield


# Simiulate a successful config flow.
# Note that we use the `bypass_validate_step_user` fixture here because
# we want the config flow validation to succeed during the test.
# pylint: disable=unused-argument
async def test_successful_config_flow(hass: HomeAssistant, bypass_validate_step_user):
    """Test a successful config flow."""
    # Initialize a config flow
    result: Dict[str, Any] = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == FlowResultType.FORM  # From HA 2022.7
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG_ALL
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Ferroamp Operation Settings"
    assert result["data"] == MOCK_CONFIG_ALL
    if "errors" in result.keys():
        assert len(result["errors"]) == 0
    assert result["result"]


# Simiulate an unsuccessful config flow
async def test_unsuccessful_config_flow(hass: HomeAssistant):
    """Test an usuccessful config flow."""

    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == FlowResultType.FORM  # From HA 2022.7
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG_ALL
    )

    # Check that the config flow is not complete and that there are errors
    # TODO: assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    # TODO: assert result["step_id"] == "user"
    # TODO: assert len(result["errors"]) > 0


# Simulate a successful option flow
async def test_successful_config_flow_option(hass: HomeAssistant):
    """Test a option flow."""

    config_entry: config_entries.ConfigEntry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test"
    )
    config_entry.add_to_hass(hass)

    # Initialize a option flow
    result = await hass.config_entries.options.async_init(
        handler="test", context={"source": "init"}
    )

    # Check that the option flow shows the init form
    assert result["type"] == FlowResultType.FORM  # From HA 2022.7
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=MOCK_OPTIONS_ALL
    )

    # Check that the option flow is complete and a new entry is created with
    # the input data
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == MOCK_OPTIONS_ALL
    if "errors" in result.keys():
        assert len(result["errors"]) == 0
    assert result["result"]
