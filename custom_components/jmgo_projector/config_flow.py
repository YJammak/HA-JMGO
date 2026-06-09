"""Config flow for JMGO Projector integration."""
from __future__ import annotations

import asyncio
import logging
import socket
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)


async def async_validate_connection(hass: HomeAssistant, host: str, port: int) -> dict:
    """Test if we can connect to the projector."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=5
        )
        writer.close()
        await writer.wait_closed()
        return {"success": True}
    except (OSError, asyncio.TimeoutError) as err:
        return {"success": False, "error": str(err)}


class JMGOProjectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for JMGO Projector."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            name = user_input.get(CONF_NAME, DEFAULT_NAME)

            # Test connection
            result = await async_validate_connection(self.hass, host, port)

            if result["success"]:
                # Check if already configured
                await self.async_set_unique_id(f"{host}_{port}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_NAME: name,
                    }
                )
            else:
                errors["base"] = "cannot_connect"
                _LOGGER.error("Cannot connect to projector: %s", result["error"])

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_import(self, import_config):
        """Handle import from configuration.yaml."""
        host = import_config[CONF_HOST]
        port = import_config.get(CONF_PORT, DEFAULT_PORT)
        name = import_config.get(CONF_NAME, DEFAULT_NAME)

        await self.async_set_unique_id(f"{host}_{port}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=name,
            data={
                CONF_HOST: host,
                CONF_PORT: port,
                CONF_NAME: name,
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return JMGOProjectorOptionsFlow(config_entry)


class JMGOProjectorOptionsFlow(config_entries.OptionsFlow):
    """Handle JMGO Projector options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Update the config entry data
            new_data = {
                **self.config_entry.data,
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input[CONF_PORT],
                CONF_NAME: user_input[CONF_NAME],
            }

            # Test connection with new settings
            result = await async_validate_connection(
                self.hass,
                user_input[CONF_HOST],
                user_input[CONF_PORT]
            )

            if result["success"]:
                # Update config entry
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data=new_data,
                    title=user_input[CONF_NAME],
                )

                # Reload the integration to apply changes
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)

                return self.async_create_entry(title="", data={})
            else:
                errors["base"] = "cannot_connect"
                _LOGGER.error("Cannot connect to projector with new settings: %s", result["error"])

        # Pre-fill with current values
        current_host = self.config_entry.data.get(CONF_HOST, "")
        current_port = self.config_entry.data.get(CONF_PORT, DEFAULT_PORT)
        current_name = self.config_entry.data.get(CONF_NAME, DEFAULT_NAME)

        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default=current_host): str,
            vol.Optional(CONF_PORT, default=current_port): int,
            vol.Optional(CONF_NAME, default=current_name): str,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "current_host": current_host,
                "current_port": str(current_port),
            }
        )
