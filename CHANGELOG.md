# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0]

Per-panel control from the dashboard.

### Added

- Optional **one light entity per panel**, behind a new config entry option
  ("Create an entity per panel", off by default). Each panel gets a colour wheel
  and a brightness slider, so panels can be controlled from a dashboard as well
  as from actions. Panel state is what Home Assistant last wrote and is restored
  across restarts, because the device has no per-panel read-back; changing one
  panel rewrites the whole scene, as that is the only write the API offers, and
  rapid changes are batched into a single write. Controllers, connectors and the
  Light Panels rhythm module are skipped, since they have no LEDs.
- `nanoleaf.get_panels` action, which returns the device's panel IDs and their
  layout coordinates. The per-panel actions need IDs that the device assigns,
  and nothing surfaced them: `services.yaml` pointed at the diagnostics
  download, but diagnostics only reported a panel *count*. Diagnostics now
  includes the panel list too.

## [2.0.0]

Migrated to the `aionanoleaf2` library.

### Changed

- **Breaking:** the dependency is now
  `aionanoleaf2 @ https://github.com/latetedemelon/aionanoleaf2/archive/refs/heads/master.tar.gz`,
  replacing `aionanoleaf @ git+…/aionanoleaf.git@master`. `aionanoleaf2` is the
  lineage Home Assistant itself has shipped since 2026.3; the older
  `aionanoleaf` was dropped upstream and its last release was in 2022. Requires
  aionanoleaf2 >= 1.2.0.
- The requirement is a source archive rather than `git+https`, so installing it
  no longer needs a `git` binary inside the Home Assistant container.
- The `EffectsClient` / `LayoutClient` / `RhythmClient` wrappers are gone; the
  same calls are now methods on `Nanoleaf`, so there is nothing optional left
  to import. `hasattr` capability detection replaced the module-level imports
  that used to make an older library break the whole integration.
- `set_panel_colors` applies its colours atomically: an unknown panel ID now
  leaves the buffer untouched instead of half-written.
- `blink_panels` uses the device's temporary-display command, so the selected
  effect is never replaced and restoring it is a re-select rather than a
  best-effort guess.
- `manifest.json` declares `integration_type: device`, matching Home
  Assistant's own manifest; without it the UI presented the device as a hub.

### Fixed

- `hacs.json` declared a minimum of Home Assistant 2024.1.0, but the code uses
  `AddConfigEntryEntitiesCallback`, which is only defined from 2025.3.0, and
  PEP 695 `type` statements. HACS would happily install this where it could not
  even be parsed. Corrected to 2025.3.0.
- The orientation `number` entity is created when the device has panels rather
  than when the first orientation read happens to succeed. A transient failure
  during the first refresh used to hide the entity until the next reload.
- Nanoleaf Essentials and Matter Wi-Fi devices no longer crash the config flow
  with `KeyError: 'state'`, via the library fix.

## [1.3.0] - 2026-05-29

Links the panels to Home Assistant's media players.

### Added
- **`nanoleaf.sync_album_art` service** — samples the dominant colours of a
  media player's current album art and spreads them across the panels (via the
  Digital Twin). Works with any `media_player` (Spotify, Sonos, Music Assistant,
  …).
- **Automation blueprint** (`blueprints/automation/nanoleaf/album_art_sync.yaml`)
  — recolours the panels on every track change and optionally turns them off
  when playback stops.

### Changed
- `manifest.json` now also requires `pillow` (bundled with Home Assistant) for
  album-art colour extraction; component bumped to 1.3.0.

## [1.2.0] - 2026-05-29

Broader hardware support and music sync. Requires aionanoleaf >= 0.5.0.

### Added
- **Music sync effect** `select` — lists the device's sound-reactive effects
  (`pluginType == "rhythm"`); selecting one sets the microphone source and
  starts music sync. Created only when such effects are discovered.
- Automatic microphone/rhythm detection; the **Rhythm source** select now
  offers *Aux* only when the module reports a 3.5mm input.
- Diagnostics now include rhythm, orientation and panel capabilities.

### Changed
- `TOUCH_MODELS` broadened to Canvas + all Shapes + Elements
  (NL29/42/47/48/52).
- HomeKit discovery now includes the original Light Panels / Aurora (NL22).
- `manifest.json` requires aionanoleaf >= 0.5.0; component bumped to 1.2.0.

### Notes
- Effect discovery is best-effort (uses the `requestAll` command); if a device
  reports nothing, the Music sync effect entity is simply not created and manual
  music sync (mic source + a sound-reactive effect) still works.

## [1.1.0] - 2026-05-29

Consolidates the two prior component branches and exposes the aionanoleaf
fork's new functionality in Home Assistant.

### Added
- **Per-panel "Digital Twin" services** (panel devices):
  - `nanoleaf.set_all_panels` — set every panel to one RGB color.
  - `nanoleaf.set_panel_colors` — set individual panels by `panel_id`.
  - `nanoleaf.blink_panels` — flash a color, then restore the prior effect.
- **`number` entity** for the global panel orientation (panel devices).
- **`select` entity** for the rhythm/audio source (Microphone / Aux) and a
  **`binary_sensor`** for whether the rhythm module is active — both created
  only when the device reports a rhythm module.
- `services.yaml`, plus service/entity/exception translations and icons.

### Changed
- Coordinator now reads layout orientation and rhythm info best-effort
  (failures on devices that lack them are tolerated and logged at debug).
- `manifest.json` requirement repinned to
  `aionanoleaf.git@master` (was `@main`, which does not exist — the fork's
  default branch is `master`). Requires aionanoleaf >= 0.4.0.
- Documentation URL points at this repository; added `issue_tracker`.

### Notes
- The new features require the wired aionanoleaf fork (>= 0.4.0). Capability
  detection means non-panel devices simply won't get the panel/rhythm entities.

## [1.0.0] - 2025-01-07

### Added
- Initial release of Nanoleaf custom component
- Full Nanoleaf integration based on Home Assistant core integration
- Support for enhanced aionanoleaf fork at https://github.com/latetedemelon/aionanoleaf
- Light control (on/off, brightness, color, color temperature, effects)
- Touch gesture support for compatible models (NL29, NL42, NL52)
  - Swipe up, down, left, right gestures
- Event entities for touch gestures
- Device triggers for automation
- Identify button for locating devices
- Configuration flow for easy setup
- Automatic discovery via SSDP, Zeroconf, and HomeKit
- Diagnostics support
- HACS compatibility
- Comprehensive documentation and installation guide

### Features
- **Platform Support**:
  - Light platform with full color and effect control
  - Button platform for device identification
  - Event platform for touch gestures
  
- **Device Support**:
  - Nanoleaf Aurora (NL29)
  - Nanoleaf Canvas (NL29)
  - Nanoleaf Shapes (NL42, NL47, NL48, NL52, NL59, NL69, NL81)
  - Nanoleaf Elements
  - Nanoleaf Lines

- **Discovery Methods**:
  - SSDP (Simple Service Discovery Protocol)
  - Zeroconf/mDNS
  - HomeKit discovery
  - Manual configuration

### Technical Details
- Uses aionanoleaf fork with enhanced functionality
- Async-based coordinator for efficient updates
- Push-based event system for real-time updates
- Local control via Nanoleaf OpenAPI
- No cloud dependency required

### Documentation
- Complete README with features and examples
- Detailed installation guide
- Automation examples for touch gestures
- Troubleshooting section

[1.3.0]: https://github.com/latetedemelon/ha-nanoleaf/releases/tag/v1.3.0
[1.2.0]: https://github.com/latetedemelon/ha-nanoleaf/releases/tag/v1.2.0
[1.1.0]: https://github.com/latetedemelon/ha-nanoleaf/releases/tag/v1.1.0
[1.0.0]: https://github.com/latetedemelon/ha-nanoleaf/releases/tag/v1.0.0
