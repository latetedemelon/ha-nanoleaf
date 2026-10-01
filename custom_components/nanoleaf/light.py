"""Support for Nanoleaf Lights."""

from __future__ import annotations

from typing import Any

from aionanoleaf2 import DigitalTwin, NanoleafException, UnknownPanel
import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    ATTR_TRANSITION,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.core import HomeAssistant, SupportsResponse
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    ALBUM_ART_COLORS,
    ATTR_DURATION,
    ATTR_MEDIA_PLAYER,
    ATTR_PANEL_ID,
    ATTR_PANELS,
    ATTR_RGB_COLOR,
    DOMAIN,
    SERVICE_BLINK_PANELS,
    SERVICE_GET_PANELS,
    SERVICE_SET_ALL_PANELS,
    SERVICE_SET_PANEL_COLORS,
    SERVICE_SYNC_ALBUM_ART,
)
from .coordinator import NanoleafConfigEntry, NanoleafCoordinator
from .entity import NanoleafEntity
from .media import async_get_album_palette

RESERVED_EFFECTS = ("*Solid*", "*Static*", "*Dynamic*")
DEFAULT_NAME = "Nanoleaf"

# (R, G, B) triplet of bytes, coerced to a tuple.
_RGB = vol.All(vol.ExactSequence((cv.byte, cv.byte, cv.byte)), vol.Coerce(tuple))
# Nanoleaf brightness overlay is a 0..100 percentage, distinct from light 0..255.
_PANEL_BRIGHTNESS = vol.All(vol.Coerce(int), vol.Range(min=0, max=100))

SET_ALL_PANELS_SCHEMA = {
    vol.Required(ATTR_RGB_COLOR): _RGB,
    vol.Optional(ATTR_BRIGHTNESS): _PANEL_BRIGHTNESS,
}

SET_PANEL_COLORS_SCHEMA = {
    vol.Required(ATTR_PANELS): vol.All(
        cv.ensure_list,
        [
            vol.Schema(
                {
                    vol.Required(ATTR_PANEL_ID): cv.positive_int,
                    vol.Required(ATTR_RGB_COLOR): _RGB,
                }
            )
        ],
    ),
    vol.Optional(ATTR_BRIGHTNESS): _PANEL_BRIGHTNESS,
}

BLINK_PANELS_SCHEMA = {
    vol.Required(ATTR_RGB_COLOR): _RGB,
    vol.Optional(ATTR_DURATION, default=2.0): cv.positive_float,
    vol.Optional(ATTR_BRIGHTNESS): _PANEL_BRIGHTNESS,
}

SYNC_ALBUM_ART_SCHEMA = {
    vol.Required(ATTR_MEDIA_PLAYER): cv.entity_domain(MEDIA_PLAYER_DOMAIN),
    vol.Optional(ATTR_BRIGHTNESS): _PANEL_BRIGHTNESS,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NanoleafConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Nanoleaf light and its per-panel services."""
    async_add_entities([NanoleafLight(entry.runtime_data)])

    # Per-panel "Digital Twin" services. They are
    # registered on the light entity so they can be targeted by entity_id,
    # device_id or area_id like any other entity service.
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SET_ALL_PANELS, SET_ALL_PANELS_SCHEMA, "async_set_all_panels"
    )
    platform.async_register_entity_service(
        SERVICE_SET_PANEL_COLORS, SET_PANEL_COLORS_SCHEMA, "async_set_panel_colors"
    )
    platform.async_register_entity_service(
        SERVICE_BLINK_PANELS, BLINK_PANELS_SCHEMA, "async_blink_panels"
    )
    platform.async_register_entity_service(
        SERVICE_SYNC_ALBUM_ART, SYNC_ALBUM_ART_SCHEMA, "async_sync_album_art"
    )
    # Returns its result instead of changing anything: the per-panel services
    # need panel IDs, and this is how you find out what yours are.
    platform.async_register_entity_service(
        SERVICE_GET_PANELS,
        None,
        "async_get_panels",
        supports_response=SupportsResponse.ONLY,
    )


class NanoleafLight(NanoleafEntity, LightEntity):
    """Representation of a Nanoleaf Light."""

    _attr_supported_color_modes = {ColorMode.COLOR_TEMP, ColorMode.HS}
    _attr_supported_features = LightEntityFeature.EFFECT | LightEntityFeature.TRANSITION
    _attr_name = None
    _attr_translation_key = "light"

    def __init__(self, coordinator: NanoleafCoordinator) -> None:
        """Initialize the Nanoleaf light."""
        super().__init__(coordinator)
        self._attr_unique_id = self._nanoleaf.serial_no
        self._attr_max_color_temp_kelvin = self._nanoleaf.color_temperature_max
        self._attr_min_color_temp_kelvin = self._nanoleaf.color_temperature_min

    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        return int(self._nanoleaf.brightness * 2.55)

    @property
    def color_temp_kelvin(self) -> int | None:
        """Return the color temperature value in Kelvin."""
        return self._nanoleaf.color_temperature

    @property
    def effect(self) -> str | None:
        """Return the current effect."""
        # The API returns the *Solid* effect if the Nanoleaf is in HS or CT mode.
        # The effects *Static* and *Dynamic* are not supported by Home Assistant.
        # These reserved effects are implicitly set and are not in the effect_list.
        # https://forum.nanoleaf.me/docs/openapi#_byoot0bams8f
        return (
            None if self._nanoleaf.effect in RESERVED_EFFECTS else self._nanoleaf.effect
        )

    @property
    def effect_list(self) -> list[str]:
        """Return the list of supported effects."""
        return self._nanoleaf.effects_list

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._nanoleaf.is_on

    @property
    def hs_color(self) -> tuple[int, int]:
        """Return the color in HS."""
        return self._nanoleaf.hue, self._nanoleaf.saturation

    @property
    def color_mode(self) -> ColorMode | None:
        """Return the color mode of the light."""
        # According to API docs, color mode is "ct", "effect" or "hs"
        # https://forum.nanoleaf.me/docs/openapi#_4qgqrz96f44d
        if self._nanoleaf.color_mode == "ct":
            return ColorMode.COLOR_TEMP
        # Home Assistant does not have an "effect" color mode, just report hs
        return ColorMode.HS

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        hs_color = kwargs.get(ATTR_HS_COLOR)
        color_temp_kelvin = kwargs.get(ATTR_COLOR_TEMP_KELVIN)
        effect = kwargs.get(ATTR_EFFECT)
        transition = kwargs.get(ATTR_TRANSITION)

        if effect:
            if effect not in self.effect_list:
                raise ValueError(
                    f"Attempting to apply effect not in the effect list: '{effect}'"
                )
            await self._nanoleaf.set_effect(effect)
        elif hs_color:
            hue, saturation = hs_color
            await self._nanoleaf.set_hue(int(hue))
            await self._nanoleaf.set_saturation(int(saturation))
        elif color_temp_kelvin:
            await self._nanoleaf.set_color_temperature(color_temp_kelvin)
        if transition:
            if brightness:  # tune to the required brightness in n seconds
                await self._nanoleaf.set_brightness(
                    int(brightness / 2.55), transition=int(kwargs[ATTR_TRANSITION])
                )
            else:  # If brightness is not specified, assume full brightness
                await self._nanoleaf.set_brightness(100, transition=int(transition))
        else:  # If no transition is occurring, turn on the light
            await self._nanoleaf.turn_on()
            if brightness:
                await self._nanoleaf.set_brightness(int(brightness / 2.55))
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        transition: float | None = kwargs.get(ATTR_TRANSITION)
        await self._nanoleaf.turn_off(None if transition is None else int(transition))
        await self.coordinator.async_refresh()

    # --- Per-panel "Digital Twin" services -------------------------------- #

    async def _async_twin(self) -> DigitalTwin:
        """Build a Digital Twin, mapping library errors to HA errors."""
        # Checked up front so that a device without addressable panels gets the
        # specific message rather than a generic library failure.
        if not self.coordinator.has_panels:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_panels",
            )
        try:
            return await self._nanoleaf.digital_twin()
        except NanoleafException as err:
            raise HomeAssistantError(str(err)) from err

    async def async_set_all_panels(
        self,
        rgb_color: tuple[int, int, int],
        brightness: int | None = None,
    ) -> None:
        """Set every panel to a single colour."""
        twin = await self._async_twin()
        twin.set_all(rgb_color)
        await self._async_sync(twin, brightness)

    async def async_set_panel_colors(
        self,
        panels: list[dict[str, Any]],
        brightness: int | None = None,
    ) -> None:
        """Set individual panel colours. Unlisted panels are turned off."""
        twin = await self._async_twin()
        colors = {panel[ATTR_PANEL_ID]: panel[ATTR_RGB_COLOR] for panel in panels}
        # Validated here rather than relying on the library's message, so the
        # user gets the translated error listing which IDs their device has.
        unknown = sorted(set(colors) - set(twin.panel_ids))
        if unknown:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="unknown_panels",
                translation_placeholders={
                    "panels": ", ".join(str(p) for p in unknown),
                    "valid": ", ".join(str(p) for p in twin.panel_ids),
                },
            )
        twin.set_colors(colors)
        await self._async_sync(twin, brightness)

    async def async_blink_panels(
        self,
        rgb_color: tuple[int, int, int],
        duration: float = 2.0,
        brightness: int | None = None,
    ) -> None:
        """Briefly show a colour on all panels, then restore the prior effect."""
        twin = await self._async_twin()
        twin.set_all(rgb_color)
        try:
            # Uses the device's temporary-display command, so the selected
            # effect is never replaced and restoring it is just a re-select.
            await twin.show_temporarily(duration, brightness=brightness)
        except NanoleafException as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()

    async def async_sync_album_art(
        self, media_player: str, brightness: int | None = None
    ) -> None:
        """Paint the panels with the dominant colours of a player's album art."""
        try:
            palette = await async_get_album_palette(
                self.hass, media_player, ALBUM_ART_COLORS
            )
        except ValueError as err:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="unknown_media_player",
                translation_placeholders={"entity_id": media_player},
            ) from err
        if not palette:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_album_art",
                translation_placeholders={"entity_id": media_player},
            )
        twin = await self._async_twin()
        twin.set_colors(
            {
                panel_id: palette[index % len(palette)]
                for index, panel_id in enumerate(twin.panel_ids)
            }
        )
        await self._async_sync(twin, brightness)

    async def async_get_panels(self) -> dict[str, Any]:
        """Return this device's panels, so their IDs can be used elsewhere.

        Sorted by ID, which is the order the per-panel services address them
        in, and includes each panel's position so a layout can be worked out
        without guessing.
        """
        panels = sorted(self._nanoleaf.panels, key=lambda panel: panel.id)
        return {
            "count": len(panels),
            "panels": [
                {
                    "panel_id": panel.id,
                    "x": panel.x_coordinate,
                    "y": panel.y_coordinate,
                    "orientation": panel.orientation,
                    "shape": panel.shape.name,
                }
                for panel in panels
            ],
        }

    async def _async_sync(self, twin: DigitalTwin, brightness: int | None) -> None:
        """Write the twin's colours to the device and refresh state."""
        try:
            await twin.sync(brightness=brightness)
        except UnknownPanel as err:
            raise ServiceValidationError(str(err)) from err
        except NanoleafException as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
