"""Define the Nanoleaf data coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from aionanoleaf import (
    InvalidToken,
    LayoutClient,
    Nanoleaf,
    NanoleafException,
    RhythmClient,
    Unavailable,
)
from aiohttp import ClientError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

type NanoleafConfigEntry = ConfigEntry[NanoleafCoordinator]

# Errors that should not abort the whole refresh when reading optional data.
_OPTIONAL_ERRORS = (NanoleafException, ClientError, OSError, ValueError)


class NanoleafCoordinator(DataUpdateCoordinator[None]):
    """Class to manage fetching Nanoleaf data."""

    config_entry: NanoleafConfigEntry

    def __init__(
        self, hass: HomeAssistant, config_entry: NanoleafConfigEntry, nanoleaf: Nanoleaf
    ) -> None:
        """Initialize the Nanoleaf data coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name="Nanoleaf",
            update_interval=timedelta(minutes=1),
        )
        self.nanoleaf = nanoleaf
        # Helper clients from the aionanoleaf fork (share the same transport).
        self.layout = LayoutClient(nanoleaf)
        self.rhythm_client = RhythmClient(nanoleaf)
        # Optional state populated best-effort by _async_update_data.
        self.global_orientation: int | None = None
        self.rhythm: dict[str, Any] = {}

    async def _async_update_data(self) -> None:
        try:
            await self.nanoleaf.get_info()
        except Unavailable as err:
            raise UpdateFailed from err
        except InvalidToken as err:
            raise ConfigEntryAuthFailed from err
        await self._async_update_optional()

    async def _async_update_optional(self) -> None:
        """Read layout/rhythm extras, tolerating devices that lack them."""
        try:
            self.global_orientation = await self.layout.get_global_orientation()
        except _OPTIONAL_ERRORS as err:
            _LOGGER.debug("Nanoleaf global orientation unavailable: %s", err)
        try:
            self.rhythm = await self.rhythm_client.get_info()
        except _OPTIONAL_ERRORS as err:
            _LOGGER.debug("Nanoleaf rhythm info unavailable: %s", err)

    @property
    def has_panels(self) -> bool:
        """Return whether the device exposes individually addressable panels."""
        return bool(getattr(self.nanoleaf, "panels", None))

    @property
    def has_rhythm(self) -> bool:
        """Return whether the device exposes a rhythm/audio module."""
        if not self.rhythm:
            return False
        connected = self.rhythm.get("rhythmConnected")
        if connected is not None:
            return bool(connected)
        return "rhythmMode" in self.rhythm or "rhythmActive" in self.rhythm
