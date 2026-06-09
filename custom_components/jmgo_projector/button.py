"""Button platform for JMGO Projector remote control."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, COMMANDS

_LOGGER = logging.getLogger(__name__)

# Button definitions: (key, name, icon)
BUTTON_DEFINITIONS = [
    ("power", "Power", "mdi:power"),
    ("ok", "OK", "mdi:checkbox-marked-circle"),
    ("return", "Return", "mdi:arrow-left"),
    ("up", "Up", "mdi:chevron-up"),
    ("down", "Down", "mdi:chevron-down"),
    ("left", "Left", "mdi:chevron-left"),
    ("right", "Right", "mdi:chevron-right"),
    ("setting", "Settings", "mdi:cog"),
    ("mongo", "Menu", "mdi:menu"),
    ("option", "Option", "mdi:format-list-bulleted"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JMGO Projector buttons from a config entry."""
    config = hass.data[DOMAIN][entry.entry_id]

    # Get the media player entity to access its send command method
    entities = []
    for key, name, icon in BUTTON_DEFINITIONS:
        entities.append(
            JMGOProjectorButton(config, key, name, icon)
        )

    async_add_entities(entities, True)


class JMGOProjectorButton(ButtonEntity):
    """Representation of a JMGO Projector remote button."""

    def __init__(self, config: dict, key: str, name: str, icon: str):
        """Initialize the button."""
        self._host = config["host"]
        self._port = config["port"]
        self._key = key
        self._attr_name = f"{config['name']} {name}"
        self._attr_unique_id = f"{config['host']}_{config['port']}_{key}"
        self._attr_icon = icon

    async def async_press(self) -> None:
        """Handle the button press."""
        import asyncio

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=5
            )

            # Send press + release
            commands = COMMANDS[self._key]
            for cmd in commands:
                writer.write(cmd)
                await asyncio.sleep(0.1)

            writer.close()
            await writer.wait_closed()

            _LOGGER.debug("Pressed button: %s", self._key)
        except (OSError, asyncio.TimeoutError) as err:
            _LOGGER.error("Error pressing button %s: %s", self._key, err)
