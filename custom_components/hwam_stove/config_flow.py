"""Config flow for HWAM Smart Control integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .api import HWAMApi, CannotConnect, InvalidResponse
from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HWAM Smart Control."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> HWAMOptionsFlow:
        """Get the options flow for this handler."""
        return HWAMOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Validate the connection
                api = HWAMApi(user_input[CONF_HOST])
                if await api.test_connection():
                    await self.async_set_unique_id(user_input[CONF_HOST])
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data=user_input,
                    )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidResponse:
                errors["base"] = "invalid_response"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            finally:
                await api.close()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                }
            ),
            errors=errors,
        )

    async def async_step_zeroconf(self, discovery_info: dict[str, Any]) -> FlowResult:
        """Handle zeroconf discovery."""
        host = discovery_info["host"]
        name = discovery_info.get("name", DEFAULT_NAME)

        await self.async_set_unique_id(host)
        self._abort_if_unique_id_configured()

        # Check if we can connect
        api = HWAMApi(host)
        try:
            if not await api.test_connection():
                return self.async_abort(reason="cannot_connect")
        except Exception:  # pylint: disable=broad-except
            return self.async_abort(reason="cannot_connect")
        finally:
            await api.close()

        return await self.async_step_user(
            {
                CONF_HOST: host,
                CONF_NAME: name,
            }
        )


class HWAMOptionsFlow(config_entries.OptionsFlow):
    """Handle HWAM options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "update_interval",
                        default=self.config_entry.options.get(
                            "update_interval", DEFAULT_UPDATE_INTERVAL.total_seconds()
                        ),
                    ): vol.All(cv.positive_int, vol.Clamp(min=10)),
                    vol.Optional(
                        "night_mode_enabled",
                        default=self.config_entry.options.get(
                            "night_mode_enabled", False
                        ),
                    ): bool,
                }
            ),
        )
