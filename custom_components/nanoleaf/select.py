"""Support for selecting the Nanoleaf rhythm/audio source."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import RHYTHM_INT_TO_MODE, RHYTHM_MODES
from .coordinator import NanoleafConfigEntry, NanoleafCoordinator
from .entity import NanoleafEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NanoleafConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Nanoleaf rhythm-mode select when supported."""
    coordinator = entry.runtime_data
    if coordinator.has_rhythm:
        async_add_entities([NanoleafRhythmModeSelect(coordinator)])


class NanoleafRhythmModeSelect(NanoleafEntity, SelectEntity):
    """Representation of the Nanoleaf rhythm source (microphone/aux)."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "rhythm_mode"
    _attr_options = RHYTHM_MODES

    def __init__(self, coordinator: NanoleafCoordinator) -> None:
        """Initialize the rhythm-mode select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._nanoleaf.serial_no}_rhythm_mode"

    @property
    def current_option(self) -> str | None:
        """Return the currently selected rhythm source."""
        mode = self.coordinator.rhythm.get("rhythmMode")
        if isinstance(mode, bool) or not isinstance(mode, int):
            return None
        return RHYTHM_INT_TO_MODE.get(mode)

    async def async_select_option(self, option: str) -> None:
        """Change the rhythm source."""
        await self.coordinator.rhythm_client.set_mode(option)
        await self.coordinator.async_request_refresh()
