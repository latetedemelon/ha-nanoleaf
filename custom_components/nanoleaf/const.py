"""Constants for Nanoleaf integration."""

DOMAIN = "nanoleaf"

NANOLEAF_EVENT = f"{DOMAIN}_event"

TOUCH_MODELS = {"NL29", "NL42", "NL52"}

TOUCH_GESTURE_TRIGGER_MAP = {
    2: "swipe_up",
    3: "swipe_down",
    4: "swipe_left",
    5: "swipe_right",
}

# Rhythm / audio-module modes (aionanoleaf RhythmClient).
RHYTHM_MODE_MICROPHONE = "microphone"
RHYTHM_MODE_AUX = "aux"
RHYTHM_MODES = [RHYTHM_MODE_MICROPHONE, RHYTHM_MODE_AUX]
RHYTHM_MODE_TO_INT = {RHYTHM_MODE_MICROPHONE: 0, RHYTHM_MODE_AUX: 1}
RHYTHM_INT_TO_MODE = {0: RHYTHM_MODE_MICROPHONE, 1: RHYTHM_MODE_AUX}

# Per-panel "Digital Twin" services (registered on the light entity).
SERVICE_SET_ALL_PANELS = "set_all_panels"
SERVICE_SET_PANEL_COLORS = "set_panel_colors"
SERVICE_BLINK_PANELS = "blink_panels"

# Service field names. ``brightness`` and ``transition`` reuse the light
# platform's constants (same string keys) and are not redefined here.
ATTR_RGB_COLOR = "rgb_color"
ATTR_PANELS = "panels"
ATTR_PANEL_ID = "panel_id"
ATTR_DURATION = "duration"
