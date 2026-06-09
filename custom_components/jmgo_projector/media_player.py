"""Media player platform for JMGO Projector."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import entity_platform

from .const import (
    DOMAIN,
    COMMANDS,
    VOLUME_CMD_MIN,
    VOLUME_CMD_MID,
    VOLUME_CMD_MAX,
    VALID_KEYS,
    SERVICE_SEND_KEY,
)

_LOGGER = logging.getLogger(__name__)

SUPPORT_JMGO = (
    MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_STEP
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JMGO Projector media player from a config entry."""
    config = hass.data[DOMAIN][entry.entry_id]
    entity = JMGOProjectorMediaPlayer(config)
    async_add_entities([entity], True)

    # Register entity service
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SEND_KEY,
        {
            vol.Required("key"): vol.In(VALID_KEYS),
        },
        "async_send_key",
    )


class JMGOProjectorMediaPlayer(MediaPlayerEntity):
    """Representation of a JMGO Projector as a media player."""

    def __init__(self, config: dict):
        """Initialize the projector."""
        self._host = config["host"]
        self._port = config["port"]
        self._attr_name = config["name"]
        self._attr_unique_id = f"{self._host}_{self._port}"
        self._attr_state = None
        self._attr_volume_level = 0.5  # Default to 50%

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Return the features supported by this entity."""
        return SUPPORT_JMGO

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the state of the entity."""
        return self._attr_state

    @property
    def volume_level(self) -> float | None:
        """Return the volume level of the media player (0..1)."""
        return self._attr_volume_level

    async def _send_command(self, commands: list[bytes], delay: float = 0.1) -> None:
        """Send command to projector."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=5
            )

            for cmd in commands:
                writer.write(cmd)
                await asyncio.sleep(delay)

            writer.close()
            await writer.wait_closed()
        except (OSError, asyncio.TimeoutError) as err:
            _LOGGER.error("Error sending command to projector: %s", err)

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        await self._send_command(COMMANDS["power_on"])
        self._attr_state = MediaPlayerState.ON
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Turn the media player off."""
        await self._send_command(COMMANDS["power_off"])
        self._attr_state = MediaPlayerState.OFF
        self.async_write_ha_state()

    async def async_volume_up(self) -> None:
        """Turn volume up."""
        new_volume = min(1.0, self._attr_volume_level + 0.1)
        await self.async_set_volume_level(new_volume)

    async def async_volume_down(self) -> None:
        """Turn volume down."""
        new_volume = max(0.0, self._attr_volume_level - 0.1)
        await self.async_set_volume_level(new_volume)

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level (0..1)."""
        # Convert 0-1 to 0-100
        volume_int = int(volume * 100)

        if volume_int < 10:
            cmd = VOLUME_CMD_MIN.copy()
            cmd[5] = bytes(str(volume_int), 'utf-8')
        elif volume_int == 100:
            cmd = VOLUME_CMD_MAX
        else:
            cmd = VOLUME_CMD_MID.copy()
            cmd[5] = bytes(str(volume_int), 'utf-8')

        # Flatten and concatenate
        full_cmd = b"".join(cmd)

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=5
            )
            writer.write(full_cmd)
            writer.close()
            await writer.wait_closed()

            self._attr_volume_level = volume
            self.async_write_ha_state()
        except (OSError, asyncio.TimeoutError) as err:
            _LOGGER.error("Error setting volume: %s", err)

    async def async_send_key(self, key: str) -> None:
        """Send a key press to the projector."""
        key_map = {
            "power": ("power_on", None),
            "return": ("return_on", "return_off"),
            "setting": ("setting_on", "setting_off"),
            "ok": ("ok_on", "ok_off"),
            "up": ("up_on", "up_off"),
            "down": ("down_on", "down_off"),
            "left": ("left_on", "left_off"),
            "right": ("right_on", "right_off"),
            "option": ("option_on", "option_off"),
            "mongo": ("mongo_on", "mongo_off"),
        }

        if key not in key_map:
            _LOGGER.error("Unknown key: %s", key)
            return

        on_cmd, off_cmd = key_map[key]

        if off_cmd is None:
            # Power toggle - just send on command
            if key == "power":
                await self._send_command(COMMANDS[on_cmd])
                if self._attr_state == MediaPlayerState.OFF:
                    self._attr_state = MediaPlayerState.ON
                else:
                    self._attr_state = MediaPlayerState.OFF
                self.async_write_ha_state()
        else:
            # Send press + release
            await self._send_command(COMMANDS[on_cmd] + COMMANDS[off_cmd])
