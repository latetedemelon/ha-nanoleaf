"""Support for the Nanoleaf global panel orientation."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import DEGREE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import NanoleafConfigEntry, NanoleafCoordinator
from .entity import NanoleafEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NanoleafConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Nanoleaf orientation number for panel devices."""
    coordinator = entry.runtime_data
    if coordinator.has_panels and coordinator.global_orientation is not None:
        async_add_entities([NanoleafOrientationNumber(coordinator)])


class NanoleafOrientationNumber(NanoleafEntity, NumberEntity):
    """Representation of the Nanoleaf global layout orientation."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "global_orientation"
    _attr_native_min_value = 0
    _attr_native_max_value = 360
    _attr_native_step = 1
    _attr_native_unit_of_measurement = DEGREE
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: NanoleafCoordinator) -> None:
        """Initialize the orientation number."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._nanoleaf.serial_no}_global_orientation"

    @property
    def native_value(self) -> float | None:
        """Return the current global orientation in degrees."""
        if self.coordinator.global_orientation is None:
            return None
        return float(self.coordinator.global_orientation)

    async def async_set_native_value(self, value: float) -> None:
        """Set a new global orientation."""
        await self.coordinator.layout.set_global_orientation(int(value))
        await self.coordinator.async_request_refresh()
