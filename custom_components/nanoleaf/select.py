"""Support for selecting the Nanoleaf rhythm source and music-sync effect."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import RHYTHM_INT_TO_MODE, RHYTHM_MODE_MICROPHONE, RHYTHM_MODES
from .coordinator import NanoleafConfigEntry, NanoleafCoordinator
from .entity import NanoleafEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NanoleafConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Nanoleaf rhythm-mode and music-sync selects when supported."""
    coordinator = entry.runtime_data
    entities: list[NanoleafEntity] = []
    if coordinator.has_rhythm:
        entities.append(NanoleafRhythmModeSelect(coordinator))
        # Only offer a music-sync effect picker if we actually discovered some.
        if coordinator.rhythm_effects:
            entities.append(NanoleafMusicEffectSelect(coordinator))
    async_add_entities(entities)


class NanoleafRhythmModeSelect(NanoleafEntity, SelectEntity):
    """Representation of the Nanoleaf rhythm source (microphone/aux)."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "rhythm_mode"

    def __init__(self, coordinator: NanoleafCoordinator) -> None:
        """Initialize the rhythm-mode select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._nanoleaf.serial_no}_rhythm_mode"

    @property
    def options(self) -> list[str]:
        """Microphone is always available; aux only when the module exposes it."""
        if self.coordinator.aux_available:
            return RHYTHM_MODES
        return [RHYTHM_MODE_MICROPHONE]

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


class NanoleafMusicEffectSelect(NanoleafEntity, SelectEntity):
    """Pick a sound-reactive effect; selecting one starts music sync.

    Choosing an effect switches the rhythm source to the microphone and
    selects that effect, so the panels react to music in the room.
    """

    _attr_translation_key = "music_effect"

    def __init__(self, coordinator: NanoleafCoordinator) -> None:
        """Initialize the music-sync effect select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._nanoleaf.serial_no}_music_effect"

    @property
    def options(self) -> list[str]:
        """Return the discovered sound-reactive effect names."""
        return self.coordinator.rhythm_effects or []

    @property
    def current_option(self) -> str | None:
        """Return the active effect if it is a sound-reactive one."""
        effect = self._nanoleaf.effect
        return effect if effect in self.options else None

    async def async_select_option(self, option: str) -> None:
        """Switch to the microphone and select the sound-reactive effect."""
        await self.coordinator.rhythm_client.set_mode(RHYTHM_MODE_MICROPHONE)
        await self._nanoleaf.set_effect(option)
        await self.coordinator.async_request_refresh()
