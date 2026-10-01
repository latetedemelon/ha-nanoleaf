"""Diagnostics support for Nanoleaf."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant

from .coordinator import NanoleafConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    config_entry: NanoleafConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = config_entry.runtime_data
    device = coordinator.nanoleaf

    return {
        "info": async_redact_data(config_entry.as_dict(), (CONF_TOKEN, "title")),
        "data": {
            "brightness_max": device.brightness_max,
            "brightness_min": device.brightness_min,
            "brightness": device.brightness,
            "color_mode": device.color_mode,
            "color_temperature_max": device.color_temperature_max,
            "color_temperature_min": device.color_temperature_min,
            "color_temperature": device.color_temperature,
            "effect": device.effect,
            "effects_list": device.effects_list,
            "firmware_version": device.firmware_version,
            "hardware_version": device.hardware_version,
            "model": device.model,
            "hue_max": device.hue_max,
            "hue_min": device.hue_min,
            "hue": device.hue,
            "is_on": device.is_on,
            "manufacturer": device.manufacturer,
            "port": device.port,
            "saturation_max": device.saturation_max,
            "saturation_min": device.saturation_min,
            "saturation": device.saturation,
            "serial_no": device.serial_no,
        },
        "panels": [
            {
                "panel_id": panel.id,
                "x": panel.x_coordinate,
                "y": panel.y_coordinate,
                "orientation": panel.orientation,
                "shape": panel.shape.name,
            }
            for panel in sorted(device.panels, key=lambda panel: panel.id)
        ],
        "capabilities": {
            "has_panels": coordinator.has_panels,
            "panel_count": len(device.panels),
            "global_orientation": coordinator.global_orientation,
            "has_rhythm": coordinator.has_rhythm,
            "library_supports_extras": coordinator.supports_extras,
            "aux_available": coordinator.supports_extras
            and device.rhythm_aux_available,
            "rhythm": device.rhythm if coordinator.supports_extras else {},
            "rhythm_effects": coordinator.rhythm_effects,
        },
    }
