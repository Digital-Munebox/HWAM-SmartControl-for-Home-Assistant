"""Test the config flow."""
from unittest.mock import patch

import pytest

from homeassistant import config_entries, data_entry_flow
from custom_components.hwam_stove.const import DOMAIN
from custom_components.hwam_stove.config_flow import ConfigFlow

async def test_form(hass):
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

    with patch(
        "custom_components.hwam_stove.config_flow.HWAMApi.test_connection",
        return_value=True,
    ), patch(
        "custom_components.hwam_stove.async_setup_entry",
        return_value=True,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "192.168.1.100",
                "name": "Test Stove",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == "create_entry"
    assert result2["title"] == "Test Stove"
    assert result2["data"] == {
        "host": "192.168.1.100",
        "name": "Test Stove",
    }

async def test_form_invalid_host(hass):
    """Test we handle invalid host."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.hwam_stove.config_flow.HWAMApi.test_connection",
        return_value=False,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "invalid_host",
                "name": "Test Stove",
            },
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "cannot_connect"}
