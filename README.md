# ha-nanoleaf

Custom Home Assistant component for Nanoleaf that uses an enhanced fork of aionanoleaf2 with additional functionality.

## Description

This is a custom component for Home Assistant that provides Nanoleaf smart
lighting integration. It uses a fork of the `aionanoleaf2` library at
[github.com/latetedemelon/aionanoleaf2](https://github.com/latetedemelon/aionanoleaf2),
which adds per-panel control, audio-module support and layout rotation on top of
fixes for Nanoleaf Essentials and Matter Wi-Fi devices, link-local IPv6 and
touch streaming.

Home Assistant's own Nanoleaf integration has required `aionanoleaf2` since
2026.3, and currently pins `1.0.2` — the release with the `KeyError: 'state'`
crash on Essentials and Matter Wi-Fi devices. This component points at the fork
instead, so that crash is fixed along with everything else.

## Features

- Full Nanoleaf integration with Home Assistant
- Support for Nanoleaf Aurora, Canvas, Shapes, and other models
- Light control (on/off, brightness, color, effects)
- **Per-panel color control** via the `nanoleaf.set_all_panels`,
  `nanoleaf.set_panel_colors` and `nanoleaf.blink_panels` services
  (powered by the fork's Digital Twin)
- **Panel orientation** control (`number` entity) for panel devices
- **Music sync** — automatic microphone detection, rhythm source select,
  "active" binary sensor, and a sound-reactive **Music sync effect** picker
- **Media-player album-art sync** — colour the panels from the now-playing
  album cover of any `media_player` (Spotify/Sonos/Music Assistant/…), via a
  service and an importable automation blueprint
- Touch gesture support for Canvas, Shapes and Elements (NL29/42/47/48/52)
- Works with any OpenAPI device (Aurora/NL22 through Lines/NL59)
- Device triggers and events
- Automatic discovery via SSDP and Zeroconf
- Configuration flow for easy setup
- Diagnostics support (includes mic/rhythm + panel capabilities)

> **Dependency note:** the per-panel, orientation, rhythm and music-sync
> features need `aionanoleaf2` >= 1.2.0. `manifest.json` points at the fork's
> `master` as a source archive, which Home Assistant installs from GitHub on
> setup — an archive URL rather than `git+https`, so no `git` binary is needed
> inside the container. Pin to a tagged release once one is published if you
> want reproducible installs.
>
> If an older `aionanoleaf2` is somehow installed, the integration degrades to
> the plain light rather than failing to load: the rhythm and orientation
> entities are simply not created.

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

### One entity per panel (optional)

By default the device appears as a single `light` entity, and panels are
addressed through the actions below. If you want to click individual panels in
the dashboard, turn on per-panel entities:

**Settings → Devices & services → Nanoleaf → Configure → Create an entity per
panel**

You get one `light` entity per addressable panel — `Panel 4231`, `Panel 12044`
and so on — each with a colour wheel and a brightness slider, controllable from
a dashboard or from a script:

```yaml
action: light.turn_on
target:
  entity_id: light.shapes_panel_4231
data:
  rgb_color: [255, 0, 0]
  brightness: 200
```

```yaml
# Several panels at once still works; each is an ordinary light entity
action: light.turn_on
target:
  entity_id:
    - light.shapes_panel_4231
    - light.shapes_panel_12044
data:
  hs_color: [240, 100]
```

Each panel entity also carries its `panel_id`, `x`, `y` and `shape` as
attributes, so a template can find panels by position.

Controllers and connectors are skipped — `Shapes Controller`, `Controller Cap`,
`Lines Connector`, `Power Connector`, and the Light Panels `Rhythm` module. They
appear in the layout but have no LEDs. Every panel the device reports is still
listed by `nanoleaf.get_panels`, so you can see what was left out.

#### What to expect from per-panel entities

These are worth understanding before relying on them, because the hardware
constrains what is possible:

- **Their state is what Home Assistant last wrote, not what the panel is
  showing.** Nanoleaf has no per-panel read-back; the device cannot be asked
  what colour a given panel is. State is restored across restarts for the same
  reason.
- **Changing one panel rewrites the whole scene,** because that is the only
  write the API offers. Rapid changes are batched, so a script setting ten
  panels produces one device write rather than ten.
- **Selecting an effect makes them stale.** An effect takes over the panels, and
  Home Assistant has no way to know what each one is showing. The next panel
  change rewrites the scene and the entities become true again.
- They are off by default because a 30-panel wall would otherwise add 30
  entities for everyone, including people who only want the device light.

The actions below need none of this and write the whole layout in one call,
which is what the hardware actually does — so prefer them for automations that
set many panels at once.

### Finding your panel IDs

The per-panel actions need panel IDs, and they are assigned by the device rather
than being 1, 2, 3. Call the **Get panels** action to list them — it returns its
result instead of changing anything, so it is safe to run from
**Developer Tools → Actions**:

```yaml
action: nanoleaf.get_panels
target:
  entity_id: light.shapes
```

```yaml
count: 4
panels:
  - panel_id: 4231
    x: 0
    y: 0
    orientation: 0
    shape: Hexagon (Shapes)
  - panel_id: 8190
    x: 200
    y: 0
    orientation: 120
    shape: Hexagon (Shapes)
  - panel_id: 12044
    x: 100
    y: 58
    orientation: 60
    shape: Hexagon (Shapes)
  - panel_id: 65533
    x: 300
    y: 58
    orientation: 0
    shape: Shapes Controller
```

`x` and `y` are the device's own layout coordinates, so you can work out which
physical panel is which rather than guessing. Watch for entries whose `shape` is
a controller or connector — `Shapes Controller`, `Controller Cap`,
`Lines Connector`, `Power Connector`. Those appear in the layout but have no
LEDs, so colours written to them do nothing.

The same list is in the integration's diagnostics download if you prefer a file.

### Actions

| Action | Description |
| --- | --- |
| `nanoleaf.get_panels` | List panel IDs and positions. Returns a result; changes nothing. |
| `nanoleaf.set_all_panels` | Set every panel to one RGB color (static scene). |
| `nanoleaf.set_panel_colors` | Set individual panels by `panel_id`. Unlisted panels are turned off. |
| `nanoleaf.blink_panels` | Briefly flash a color on all panels, then restore the previous effect. |
| `nanoleaf.sync_album_art` | Colour the panels from a media player's album art. |

Because a static scene describes the whole layout, `set_panel_colors` turns off
any panel you do not list. To change some panels and leave the others as they
are, include them all and repeat their current colours.

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
  created only when the device has a rhythm module. Aux is only offered when
  the module actually has a 3.5mm input.
- **Rhythm active** (`binary_sensor.<device>_rhythm_active`) — whether the
  rhythm module is currently active.
- **Music sync effect** (`select.<device>_music_sync_effect`) — see below.

## Music sync

Nanoleaf panels react to music using the device **microphone** (built-in on
Canvas, Shapes, Elements and Lines; an add-on Rhythm module on the original
Light Panels/Aurora). The integration detects this automatically:

- If your device has a microphone/rhythm module, the **Rhythm source**,
  **Rhythm active** and (when sound-reactive effects are found) **Music sync
  effect** entities appear. If they don't appear, the device has no mic.
- The integration discovers the device's **sound-reactive effects**
  (`pluginType == "rhythm"`). Selecting one from the **Music sync effect**
  entity switches the source to the microphone and starts music sync:

```yaml
# Start music sync with a sound-reactive effect
service: select.select_option
target:
  entity_id: select.shapes_music_sync_effect
data:
  option: "Pulse Pop Beats"   # one of your device's sound-reactive effects
```

You can also do it manually: set **Rhythm source** to *Microphone* and pick a
sound-reactive effect from the light's effect list.

> The set of sound-reactive effects is read once at startup; reload the
> integration after creating new music effects in the Nanoleaf app. Effect
> discovery is best-effort — if your firmware reports effects differently the
> *Music sync effect* entity simply won't appear, and manual music sync still
> works.

## Link to Home Assistant media players (album-art sync)

Home Assistant's "music centre" is the `media_player` domain — Spotify, Sonos,
Chromecast, Apple Music, **Music Assistant**, etc. This integration can colour
your panels from whatever a media player is playing:

**Service** — `nanoleaf.sync_album_art` samples the dominant colours of the
current **album art** and spreads them across the panels:

```yaml
service: nanoleaf.sync_album_art
target:
  entity_id: light.shapes
data:
  media_player: media_player.spotify
  brightness: 80          # optional, 0-100
```

**Automatic (blueprint)** — to follow playback hands-free, import the included
blueprint. It recolours the panels on every track change and can turn them off
when the music stops:

1. In Home Assistant go to **Settings → Automations & Scenes → Blueprints →
   Import Blueprint**.
2. Paste the blueprint URL:
   `https://github.com/latetedemelon/ha-nanoleaf/blob/main/blueprints/automation/nanoleaf/album_art_sync.yaml`
3. Create an automation from it, choosing your media player and Nanoleaf light.

> Album-art colours come from the media player's artwork via Home Assistant's
> built-in image support (Pillow); a player with no artwork is reported back as
> an error. This pairs nicely with the mic-based **Music sync effect** above —
> use album-art colours for ambient mood and the mic effect for beat reactivity.

## Supported hardware

Any Nanoleaf device that speaks the local OpenAPI works (add it by IP if it
isn't auto-discovered):

- Light Panels / Aurora (NL22) — with the add-on Rhythm module for music sync
- Canvas (NL29) — touch
- Shapes: Hexagons (NL42), Triangles (NL47), Mini Triangles (NL48) — touch
- Elements (NL52) — touch
- Lines (NL59)

Touch gestures are enabled on Canvas, Shapes and Elements. Per-panel control,
orientation and rhythm entities appear only on devices that support them.

## License

MIT License - See LICENSE file for details

## Credits

Based on the official Home Assistant Nanoleaf integration with modifications to use the enhanced aionanoleaf fork.
