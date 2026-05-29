# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[1.2.0]: https://github.com/latetedemelon/ha-nanoleaf/releases/tag/v1.2.0
[1.1.0]: https://github.com/latetedemelon/ha-nanoleaf/releases/tag/v1.1.0
[1.0.0]: https://github.com/latetedemelon/ha-nanoleaf/releases/tag/v1.0.0
