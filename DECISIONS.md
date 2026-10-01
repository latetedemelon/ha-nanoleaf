# Consolidation & development notes — ha-nanoleaf

This records what was changed on `claude/ecstatic-clarke-FREgt` and why.

## Goal

"Merge all branches and take the idea as far as you can." The stated purpose of
this repo is to "utilize new functionality under my fork of aionanoleaf" inside
a Home Assistant custom component.

## Branch reconciliation

Two Copilot branches each added a near-identical copy of the **stock** Home
Assistant Nanoleaf integration (light/button/event), differing only in docs and
`manifest.json`. Crucially, **neither used any of the fork's new functionality.**

| Branch | Disposition |
| --- | --- |
| `copilot/add-custom-nanoleaf-component` (PR #1) | Merged as the base (more polished; has `SUMMARY.md`, richer README). |
| `copilot/patch-custom-component-nanoleaf` (PR #2) | Merged; conflicts resolved in favour of the add- branch, keeping its `DEVELOPMENT.md`. |

The component `.py` files were identical between the two, so the only conflicts
were docs + manifest, resolved to the add- branch versions.

## What was added (the actual "take it further")

The fork exposes per-panel (`DigitalTwin`), effects, layout and rhythm helpers.
These are now surfaced in Home Assistant:

1. **Per-panel services** on the light entity (`set_all_panels`,
   `set_panel_colors`, `blink_panels`) using `DigitalTwin`. Registered as entity
   services so they can be targeted by entity/device/area.
2. **`number` entity** — global panel orientation (`LayoutClient`).
3. **`select` entity** — rhythm source, and a **`binary_sensor`** — rhythm
   active (`RhythmClient`).
4. Coordinator extended to fetch orientation + rhythm best-effort, with
   `has_panels` / `has_rhythm` capability gating so non-panel / non-rhythm
   devices don't get irrelevant entities.

## Key decisions

- **Dropped the `transition` parameter from the panel services.** The fork's
  `DigitalTwin.sync(transition_ms=...)` writes its value straight into the
  Nanoleaf animation-data `transitionTime` field, whose unit is **not**
  milliseconds (it is the device's animation-time unit, ~deciseconds). Mapping
  HA seconds to it could produce wildly wrong transitions, and it can't be
  verified without hardware, so the services use the library default and expose
  only the unambiguous `duration` (real seconds) and `brightness` (0-100).
- **`manifest.json` requirement** repinned from `@main` (which does not exist —
  the fork's default branch is `master`) to `@master`. Requires the wired
  aionanoleaf >= 0.4.0 (merged in aionanoleaf PR #3).
- **Capability gating, not hard failure.** Devices without panels or a rhythm
  module simply don't get those entities; the per-panel services raise a clear,
  translated `ServiceValidationError` if called on an unsupported device.

## Verification

Home Assistant cannot be imported on the container's default Python 3.11
(HA 2025.x needs 3.13), so a Python 3.13 venv was created with
`homeassistant==2025.10.1` and the local wired aionanoleaf. Against that:

- All 13 component modules import cleanly.
- The three service schemas validate (RGB byte ranges, 0-100 brightness, list
  parsing, defaults).
- The Digital Twin mapping produces the correct `PUT /effects` static-scene
  payload end-to-end through the real `Nanoleaf` transport (fake aiohttp
  session).
- `has_panels` / `has_rhythm` gating and the number/select/binary_sensor value
  mapping behave correctly.
- `flake8` (E9/F) is clean; all JSON/YAML valid; service names and translation
  keys are consistent across `const.py`, `services.yaml` and `strings.json`.

## Not verified here (needs real hardware)

- Behaviour on a physical device: whether unlisted panels in `set_panel_colors`
  go black vs. retain colour, exact transition timing, and that
  `/panelLayout/globalOrientation` and `/rhythm` respond as expected on each
  model. A full HA runtime test would use
  `pytest-homeassistant-custom-component`.

## Follow-up: hardware breadth & music sync (1.2.0)

Implements the two follow-up requests ("support all hardware versions" and "wire
up music sync"). Requires aionanoleaf >= 0.5.0.

- **Hardware breadth.** `TOUCH_MODELS` broadened to Canvas + all Shapes +
  Elements (`NL29/42/47/48/52`; previously only 29/42/52). `manifest.json`
  HomeKit discovery now includes the original Light Panels/Aurora (`NL22`). The
  integration already works with any OpenAPI device added by IP; the library
  `get_info()` was also made tolerant of devices that omit a panel layout.
- **Music sync.** Research (Nanoleaf OpenAPI + openHAB + rowak) confirmed the
  reliable surface: rhythm `connected`/`active`/`mode` (0=mic, 1=aux), and that
  sound-reactive effects are identified by `pluginType == "rhythm"` via the
  `requestAll` command. Added:
  - A **Music sync effect** `select` listing the discovered sound-reactive
    effects; choosing one sets the mic source and selects the effect. Created
    only when such effects are discovered (best-effort; absent if the device
    reports nothing).
  - Rhythm source `select` now offers *Aux* only when `auxAvailable`.
  - Capability detection answers "does this device have a mic?" — the rhythm
    entities only appear when `rhythmConnected`, and diagnostics now include the
    raw rhythm/orientation/panel data.
- **Why no "music sync" switch:** there is no global music-sync on/off in the
  API — reactivity is a property of the *selected effect*. A select of
  sound-reactive effects models this honestly; a switch would have ambiguous
  on/off state.
- **Version-skew safety:** the coordinator guards `get_rhythm_effects` with
  `hasattr`, so the integration still loads if an older aionanoleaf is present.

### Verified (real HA 2025.10.1 + aionanoleaf 0.5.0, Python 3.13 venv)
All 13 modules import; rhythm-source aux-gating, music-effect select
options/current-option, capability detection, and the service schemas all pass
the logic checks. aionanoleaf side: 17 unit tests, flake8, mypy, pylint 10/10.

### Still needs real hardware
Whether `requestAll`/`pluginType` is reported as expected per firmware, and that
selecting a rhythm effect + mic actually drives music sync on the device.

## Follow-up: link to Home Assistant media players (1.3.0)

Requested: "doesn't HA have a music central area — can we link to it?" HA's music
hub is the `media_player` domain (Spotify, Sonos, Music Assistant, …). The
mic-based music sync reacts to room sound and knows nothing about HA playback, so
this bridges the now-playing data to the panels. Chosen scope: **both**
album-art colouring and playback triggering.

- **`nanoleaf.sync_album_art` service** (entity service on the light) reads the
  target `media_player`'s artwork via the **public** `MediaPlayerEntity.
  async_get_media_image()` (works across Spotify/Sonos/etc. without per-platform
  code), extracts up to 6 dominant colours with Pillow (run in an executor —
  Pillow is blocking), and spreads them round-robin across the panels via the
  Digital Twin. Clear `ServiceValidationError`s for "not a media player" / "no
  album art".
- **Playback triggering via a blueprint**, not a custom state listener / options
  flow. Rationale: a blueprint is the idiomatic, reviewable HA way to wire
  "on play / on track change / on stop" to the service, and avoids shipping
  untested lifecycle code (live listeners, unload handling). The blueprint
  recolours on `entity_picture`/`to: playing` changes and optionally turns the
  panels off on stop.
- **`pillow`** added to `manifest.json` requirements. It already ships with Home
  Assistant, so this is satisfied without a heavy reinstall; declared loosely
  (`>=10.0.0`).

### Verified (real HA 2025.10.1, Python 3.13 venv)
`MediaPlayerEntity.async_get_media_image` and `EntityComponent.get_entity` exist
and are used; `_extract_palette` returns the right colours from a generated
image; album-art colours map round-robin onto panels (checked through the real
`Nanoleaf`/Digital Twin transport); the blueprint loads with HA's YAML loader
(`!input` handled), its selectors validate, and its triggers pass
`cv.TRIGGER_SCHEMA`; all JSON/YAML valid and service/translation/icon keys
consistent.

### Still needs real hardware / runtime
End-to-end with a real media player + device (artwork fetch latency, how often
`entity_picture` changes per integration, and the on-device look of the palette).

## Migrating to aionanoleaf2 (2.0.0)

The component was wired to `latetedemelon/aionanoleaf`, a fork of
`milanmeu/aionanoleaf`. That upstream last released in 2022, and Home Assistant
replaced it with `aionanoleaf2` in core commit 8693294ea, shipped in 2026.3. So
the old lineage is a dead end: staying on it means diverging further from the
library Home Assistant actually ships, for a library nobody upstream maintains.

`aionanoleaf2` did not have the five device-API calls this component relied on
(`get/set_global_orientation`, rhythm info and mode, rhythm-effect discovery),
and its `DigitalTwin` has a different shape. Those calls were added to
`aionanoleaf2` 1.2.0 rather than reimplemented here, because they are device API
and an integration should not be hand-rolling HTTP against the panels.

Three deliberate differences from the old fork's versions:

- An absent resource is distinguished from a transport failure. The old
  `RhythmClient.get_info` did `except Exception: return {}`, which also
  swallowed real errors.
- `set_global_orientation` validates its range instead of silently clamping, so
  a caller passing degrees from the wrong source finds out.
- Durations are in seconds throughout, not milliseconds in some places.

The helper *clients* were not ported. `aionanoleaf2` is one `Nanoleaf` class
with `get_*`/`set_*` methods, and three extra wrapper classes would have been a
second idiom for no benefit. This also removed the module-level imports of
optional classes, which were the reason an older library used to stop the whole
integration from loading rather than just disabling some entities.
