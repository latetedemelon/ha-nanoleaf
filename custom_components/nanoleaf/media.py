"""Helpers for linking Nanoleaf panels to Home Assistant media players."""

from __future__ import annotations

import io
import logging

from homeassistant.components import media_player
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

RGB = tuple[int, int, int]


def _extract_palette(data: bytes, count: int) -> list[RGB]:
    """Return up to ``count`` dominant RGB colors from image bytes.

    Runs in an executor (Pillow is blocking). Colors are ordered most-dominant
    first. Returns ``[]`` if the image can't be decoded.
    """
    try:
        from PIL import Image  # noqa: PLC0415 - optional, bundled with HA
    except ImportError:  # pragma: no cover - Pillow ships with Home Assistant
        _LOGGER.warning("Pillow is not available; cannot extract album-art colors")
        return []
    try:
        with Image.open(io.BytesIO(data)) as image:
            rgb = image.convert("RGB")
            rgb.thumbnail((64, 64))  # downscale for speed
            paletted = rgb.quantize(colors=max(1, count))
            palette = paletted.getpalette() or []
            # getcolors() -> list of (pixel_count, palette_index); most common first
            ordered = sorted(paletted.getcolors() or [], reverse=True)
    except Exception as err:  # noqa: BLE001 - Pillow raises a variety of errors
        _LOGGER.debug("Could not extract album-art palette: %s", err)
        return []

    colors: list[RGB] = []
    for _pixel_count, index in ordered:
        chunk = palette[index * 3 : index * 3 + 3]
        if len(chunk) == 3:
            colors.append((chunk[0], chunk[1], chunk[2]))
    return colors


async def async_get_album_palette(
    hass: HomeAssistant, media_player_entity_id: str, count: int
) -> list[RGB]:
    """Fetch the now-playing album art for a media player and return its palette.

    Returns ``[]`` when the media player has no artwork. Raises ``ValueError`` if
    the entity is not a known media player.
    """
    component = hass.data.get(media_player.DOMAIN)
    entity = component.get_entity(media_player_entity_id) if component else None
    if entity is None:
        raise ValueError(f"{media_player_entity_id} is not a media player")

    data, _content_type = await entity.async_get_media_image()
    if not data:
        return []
    return await hass.async_add_executor_job(_extract_palette, data, count)
