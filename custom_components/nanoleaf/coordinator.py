"""Define the Nanoleaf data coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging

from aiohttp import ClientError
from aionanoleaf2 import InvalidToken, Nanoleaf, NanoleafException, Unavailable

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
        # Sound-reactive effect names; None until loaded once (heavy call).
        self.rhythm_effects: list[str] | None = None

    async def _async_update_data(self) -> None:
        try:
            await self.nanoleaf.get_info()
        except Unavailable as err:
            raise UpdateFailed from err
        except InvalidToken as err:
            raise ConfigEntryAuthFailed from err
        await self._async_update_optional()

    async def _async_update_optional(self) -> None:
        """Read layout/rhythm extras, tolerating devices that lack them.

        The library reports an absent resource rather than raising, so these
        only fail on a genuine transport problem, which must not abort the
        whole refresh.
        """
        if not self.supports_extras:
            return
        try:
            await self.nanoleaf.get_global_orientation()
        except _OPTIONAL_ERRORS as err:
            _LOGGER.debug("Nanoleaf global orientation unavailable: %s", err)
        try:
            await self.nanoleaf.get_rhythm()
        except _OPTIONAL_ERRORS as err:
            _LOGGER.debug("Nanoleaf rhythm info unavailable: %s", err)
        # Discover sound-reactive effects once, only on devices with a mic:
        # it is a full effect-metadata download.
        if self.has_rhythm and self.rhythm_effects is None:
            try:
                self.rhythm_effects = await self.nanoleaf.get_rhythm_effects()
            except _OPTIONAL_ERRORS as err:
                _LOGGER.debug("Nanoleaf rhythm effects unavailable: %s", err)
                self.rhythm_effects = []

    @property
    def supports_extras(self) -> bool:
        """Return whether the installed library exposes the rhythm/layout API.

        These arrived in aionanoleaf2 1.2.0. The requirement is a URL, so pip
        cannot enforce a floor; checking here means an older library degrades
        to the plain light instead of breaking the whole integration.
        """
        return hasattr(self.nanoleaf, "get_rhythm")

    @property
    def has_panels(self) -> bool:
        """Return whether the device exposes individually addressable panels."""
        return bool(self.nanoleaf.panels)

    @property
    def has_rhythm(self) -> bool:
        """Return whether the device exposes a rhythm/audio (mic) module."""
        return self.supports_extras and self.nanoleaf.has_rhythm

    @property
    def global_orientation(self) -> int | None:
        """Return the panel layout rotation in degrees, if known."""
        if not self.supports_extras:
            return None
        return self.nanoleaf.global_orientation
