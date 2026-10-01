"""Support for the Nanoleaf rhythm/audio module state."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import NanoleafConfigEntry, NanoleafCoordinator
from .entity import NanoleafEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NanoleafConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Nanoleaf rhythm binary sensor when supported."""
    coordinator = entry.runtime_data
    if coordinator.has_rhythm:
        async_add_entities([NanoleafRhythmActiveBinarySensor(coordinator)])


class NanoleafRhythmActiveBinarySensor(NanoleafEntity, BinarySensorEntity):
    """Representation of whether the Nanoleaf rhythm module is active."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_translation_key = "rhythm_active"

    def __init__(self, coordinator: NanoleafCoordinator) -> None:
        """Initialize the rhythm binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._nanoleaf.serial_no}_rhythm_active"

    @property
    def is_on(self) -> bool:
        """Return True if the rhythm module is currently picking up sound."""
        return self.coordinator.nanoleaf.rhythm_active
