# ha-nanoleaf

Custom Home Assistant component for Nanoleaf that uses an enhanced fork of aionanoleaf with additional functionality.

## Description

This is a custom component for Home Assistant that provides Nanoleaf smart lighting integration. It uses a fork of the `aionanoleaf` library located at [github.com/latetedemelon/aionanoleaf](https://github.com/latetedemelon/aionanoleaf) which includes additional features and improvements.

## Features

- Full Nanoleaf integration with Home Assistant
- Support for Nanoleaf Aurora, Canvas, Shapes, and other models
- Light control (on/off, brightness, color, effects)
- **Per-panel color control** via the `nanoleaf.set_all_panels`,
  `nanoleaf.set_panel_colors` and `nanoleaf.blink_panels` services
  (powered by the fork's Digital Twin)
- **Panel orientation** control (`number` entity) for panel devices
- **Rhythm / audio module** source select and an "active" binary sensor
  (when the device has a rhythm module)
- Touch gesture support for compatible models (NL29, NL42, NL52)
- Device triggers and events
- Automatic discovery via SSDP and Zeroconf
- Configuration flow for easy setup
- Diagnostics support

> **Dependency note:** the per-panel / orientation / rhythm features require the
> wired aionanoleaf fork (>= 0.4.0), which is now on `master`. The
> `manifest.json` pins the dependency to
> `aionanoleaf.git@master`; Home Assistant installs it directly from GitHub on
> setup. (Pin to a tagged release once one is published for reproducible
> installs.)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add the repository URL: `https://github.com/latetedemelon/ha-nanoleaf`
6. Select category: "Integration"
7. Click "Add"
8. Find "Nanoleaf" in the integration list and install it
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/nanoleaf` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

### Adding the Integration

1. Go to Settings → Devices & Services
2. Click "+ ADD INTEGRATION"
3. Search for "Nanoleaf"
4. Enter the IP address or hostname of your Nanoleaf device
5. Press and hold the power button on your Nanoleaf for 5 seconds until the LEDs start flashing
6. Click Submit within 30 seconds
7. Your Nanoleaf device will be added to Home Assistant

### Automatic Discovery

The integration also supports automatic discovery via:
- **SSDP**: Your Nanoleaf devices will be automatically discovered on the network
- **Zeroconf/mDNS**: Devices will appear in the integrations page
- **HomeKit**: Compatible with HomeKit discovery

Once discovered, you'll see a notification to set up the device. Follow the configuration steps above.

## Supported Devices

- Nanoleaf Aurora (NL29)
- Nanoleaf Canvas (NL29)
- Nanoleaf Shapes (NL42, NL47, NL48, NL52, NL59, NL69, NL81)
- Nanoleaf Elements
- Nanoleaf Lines

## Touch Gesture Support

For compatible models (NL29, NL42, NL52), touch gestures are supported:
- Swipe Up
- Swipe Down
- Swipe Left
- Swipe Right

These gestures can be used in automations via device triggers or event entities.

### Example Automation with Touch Gestures

```yaml
automation:
  - alias: "Nanoleaf Swipe Up"
    trigger:
      - platform: event
        event_type: nanoleaf_event
        event_data:
          type: swipe_up
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room
```

Or using the device trigger:

```yaml
automation:
  - alias: "Nanoleaf Swipe Down"
    trigger:
      - platform: device
        device_id: your_nanoleaf_device_id
        domain: nanoleaf
        type: swipe_down
    action:
      - service: light.turn_off
        target:
          entity_id: light.living_room
```

## Per-panel control & advanced features

On panel devices (Shapes, Canvas, Elements, Lines) this integration exposes the
fork's enhanced functionality.

### Services

| Service | Description |
| --- | --- |
| `nanoleaf.set_all_panels` | Set every panel to one RGB color (static scene). |
| `nanoleaf.set_panel_colors` | Set individual panels by `panel_id`. Unlisted panels are turned off. |
| `nanoleaf.blink_panels` | Briefly flash a color on all panels, then restore the previous effect. |

Panel IDs can be read from the integration's diagnostics download.

```yaml
# Paint two panels and turn the rest off
service: nanoleaf.set_panel_colors
target:
  entity_id: light.shapes
data:
  panels:
    - panel_id: 4231
      rgb_color: [255, 0, 0]
    - panel_id: 12044
      rgb_color: [0, 0, 255]
  brightness: 80
```

```yaml
# Flash all panels green for 3 seconds, then restore the prior effect
service: nanoleaf.blink_panels
target:
  entity_id: light.shapes
data:
  rgb_color: [0, 255, 0]
  duration: 3
```

### Additional entities

- **Panel orientation** (`number.<device>_panel_orientation`) — global layout
  orientation in degrees, for panel devices.
- **Rhythm source** (`select.<device>_rhythm_source`) — Microphone / Aux,
  created only when the device has a rhythm module.
- **Rhythm active** (`binary_sensor.<device>_rhythm_active`) — whether the
  rhythm module is currently active.

## License

MIT License - See LICENSE file for details

## Credits

Based on the official Home Assistant Nanoleaf integration with modifications to use the enhanced aionanoleaf fork.
