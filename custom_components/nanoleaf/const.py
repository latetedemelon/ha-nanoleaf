"""Constants for Nanoleaf integration."""

DOMAIN = "nanoleaf"

NANOLEAF_EVENT = f"{DOMAIN}_event"

# Touch-capable model prefixes: Canvas (NL29), Shapes Hexagons/Triangles/Mini
# (NL42/NL47/NL48) and Elements (NL52). Lines (NL59) and Light Panels (NL22)
# have no touch sensors.
TOUCH_MODELS = {"NL29", "NL42", "NL47", "NL48", "NL52"}

TOUCH_GESTURE_TRIGGER_MAP = {
    2: "swipe_up",
    3: "swipe_down",
    4: "swipe_left",
    5: "swipe_right",
}

# Audio source names. The library owns the mapping to the API's numbers and
# reports the sources a given module actually has, so only the fallback name
# is needed here.
RHYTHM_MODE_MICROPHONE = "microphone"

# Per-panel "Digital Twin" services (registered on the light entity).
SERVICE_SET_ALL_PANELS = "set_all_panels"
SERVICE_SET_PANEL_COLORS = "set_panel_colors"
SERVICE_BLINK_PANELS = "blink_panels"
SERVICE_SYNC_ALBUM_ART = "sync_album_art"
SERVICE_GET_PANELS = "get_panels"

# Service field names. ``brightness`` and ``transition`` reuse the light
# platform's constants (same string keys) and are not redefined here.
ATTR_RGB_COLOR = "rgb_color"
ATTR_PANELS = "panels"
ATTR_PANEL_ID = "panel_id"
ATTR_DURATION = "duration"
ATTR_MEDIA_PLAYER = "media_player"

# Number of dominant album-art colors spread across the panels.
ALBUM_ART_COLORS = 6
