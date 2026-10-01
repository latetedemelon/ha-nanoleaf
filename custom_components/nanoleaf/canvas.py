"""Shared per-panel colour state for a Nanoleaf device.

Nanoleaf has no per-panel read-back and applies panel colours as one
whole-scene write, so there is nothing to poll and no way to change a single
panel in isolation. This holds the colours Home Assistant believes each panel
has, and writes the whole set to the device when any of them changes.

Writes are coalesced: a script that sets ten panels in a row produces one
scene write rather than ten.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aionanoleaf2 import NanoleafException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer

if TYPE_CHECKING:
    from aionanoleaf2 import DigitalTwin, Panel

    from .coordinator import NanoleafCoordinator

_LOGGER = logging.getLogger(__name__)

RGB = tuple[int, int, int]
BLACK: RGB = (0, 0, 0)

# Long enough to batch a scripted run of panel calls, short enough to feel
# immediate when a single panel is changed from the UI.
WRITE_COOLDOWN = 0.3

# Shapes that appear in the layout but have no LEDs, so a colour written to
# them does nothing. Names come from aionanoleaf2's shape table.
#
# Elements corner pieces and Canvas passive squares are deliberately *not*
# listed: it is not clear they lack LEDs, and hiding a real panel is worse
# than showing one that ignores you. `nanoleaf.get_panels` lists every panel
# the device reports, so anything missing here can be accounted for.
NON_LIGHT_SHAPES = frozenset(
    {
        "Rhythm",
        "Shapes Controller",
        "Lines Connector",
        "Controller Cap",
        "Power Connector",
    }
)


class PanelCanvas:
    """The colours Home Assistant believes each panel is showing."""

    def __init__(self, hass: HomeAssistant, coordinator: NanoleafCoordinator) -> None:
        """Initialize the canvas with every addressable panel black."""
        self._coordinator = coordinator
        self._colors: dict[int, RGB] = {
            panel.id: BLACK for panel in self.addressable_panels(coordinator)
        }
        self._twin: DigitalTwin | None = None
        self._debouncer = Debouncer(
            hass,
            _LOGGER,
            cooldown=WRITE_COOLDOWN,
            immediate=True,
            function=self._async_write,
        )

    @staticmethod
    def addressable_panels(coordinator: NanoleafCoordinator) -> list[Panel]:
        """Return the panels that actually have LEDs, ordered by ID.

        The order matters: it is the order the device is written in, and the
        order `nanoleaf.get_panels` reports.
        """
        return sorted(
            (
                panel
                for panel in coordinator.nanoleaf.panels
                if panel.shape.name not in NON_LIGHT_SHAPES
            ),
            key=lambda panel: panel.id,
        )

    @property
    def panel_ids(self) -> tuple[int, ...]:
        """Return the panel IDs this canvas covers."""
        return tuple(self._colors)

    def get(self, panel_id: int) -> RGB:
        """Return the colour this panel is believed to be showing."""
        return self._colors.get(panel_id, BLACK)

    def set(self, panel_id: int, color: RGB) -> None:
        """Record a new colour for one panel, without writing anything yet."""
        if panel_id in self._colors:
            self._colors[panel_id] = color

    async def async_request_write(self) -> None:
        """Write the whole canvas to the device, coalescing rapid calls."""
        await self._debouncer.async_call()

    async def async_shutdown(self) -> None:
        """Flush any pending write and stop accepting new ones."""
        self._debouncer.async_shutdown()

    async def _async_write(self) -> None:
        """Push every panel colour to the device as a single scene."""
        if self._twin is None:
            try:
                # Restricted to the panels that have LEDs, so a controller or
                # connector is not carried in every scene write.
                self._twin = await self._coordinator.nanoleaf.digital_twin(
                    panel_ids=self.panel_ids
                )
            except NanoleafException as err:
                _LOGGER.error("Could not build the panel canvas: %s", err)
                return

        self._twin.set_colors(self._colors)
        try:
            await self._twin.sync()
        except NanoleafException as err:
            _LOGGER.error("Could not write panel colours: %s", err)
