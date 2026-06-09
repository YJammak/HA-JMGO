"""Number platform for JMGO Projector volume control."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, VOLUME_CMD_MIN, VOLUME_CMD_MID, VOLUME_CMD_MAX

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JMGO Projector number entities from a config entry."""
    config = hass.data[DOMAIN][entry.entry_id]

    entities = [
        JMGOProjectorVolume(config),
    ]

    async_add_entities(entities, True)


class JMGOProjectorVolume(NumberEntity):
    """Representation of a JMGO Projector volume control."""

    def __init__(self, config: dict):
        """Initialize the volume control."""
        self._host = config["host"]
        self._port = config["port"]
        self._attr_name = f"{config['name']} Volume"
        self._attr_unique_id = f"{config['host']}_{config['port']}_volume"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "%"
        self._attr_mode = NumberMode.SLIDER
        self._attr_native_value = 50  # Default value
        self._attr_icon = "mdi:volume-high"

    async def async_set_native_value(self, value: float) -> None:
        """Set the volume level."""
        import asyncio

        volume_int = int(value)

        # Build command based on volume level
        if volume_int < 10:
            cmd = VOLUME_CMD_MIN.copy()
            cmd[5] = bytes(str(volume_int), 'utf-8')
        elif volume_int == 100:
            cmd = VOLUME_CMD_MAX
        else:
            cmd = VOLUME_CMD_MID.copy()
            cmd[5] = bytes(str(volume_int), 'utf-8')

        full_cmd = b"".join(cmd)

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=5
            )
            writer.write(full_cmd)
            writer.close()
            await writer.wait_closed()

            self._attr_native_value = value
            # Update icon based on volume
            if value == 0:
                self._attr_icon = "mdi:volume-off"
            elif value < 30:
                self._attr_icon = "mdi:volume-low"
            elif value < 70:
                self._attr_icon = "mdi:volume-medium"
            else:
                self._attr_icon = "mdi:volume-high"

            self.async_write_ha_state()
            _LOGGER.debug("Set volume to: %d", volume_int)
        except (OSError, asyncio.TimeoutError) as err:
            _LOGGER.error("Error setting volume: %s", err)
