# Development Notes

## Purpose

This repository provides a custom Home Assistant integration for Nanoleaf devices that uses a forked version of the `aionanoleaf` library. The primary goal is to test new features and improvements before submitting pull requests to the upstream projects.

## Structure

```
ha-nanoleaf/
├── custom_components/
│   └── nanoleaf/          # The custom integration
│       ├── __init__.py    # Main integration setup
│       ├── button.py      # Button entity support
│       ├── config_flow.py # Configuration flow
│       ├── const.py       # Constants
│       ├── coordinator.py # Data coordinator
│       ├── device_trigger.py # Device trigger support
│       ├── diagnostics.py # Diagnostics support
│       ├── entity.py      # Base entity class
│       ├── event.py       # Event entity support
│       ├── icons.json     # Custom icons
│       ├── light.py       # Light entity (main component)
│       ├── manifest.json  # Integration manifest (MODIFIED)
│       └── strings.json   # Translation strings
├── hacs.json              # HACS metadata
├── README.md              # Main documentation
├── INSTALLATION.md        # Installation guide
└── CHANGELOG.md           # Version history
```

## Key Changes from Official Integration

### manifest.json

The only file that differs from the official Home Assistant core integration:

1. **requirements**: Changed from Home Assistant's pin (`aionanoleaf2==1.0.2` on 2026.3+, `aionanoleaf==0.2.1` before that) to `aionanoleaf2 @ https://github.com/latetedemelon/aionanoleaf2/archive/refs/heads/master.tar.gz`
2. **codeowners**: Changed to `@latetedemelon`
3. **documentation**: Changed to point to this repository
4. **version**: Added version field `0.1.0`

The light platform and coordinator also differ, to expose the per-panel,
rhythm and orientation features; the `binary_sensor`, `number`, `select` and
`media` modules are new. Everything else tracks the upstream integration.

## Testing Workflow

1. **Fork aionanoleaf2**: the fork is at https://github.com/latetedemelon/aionanoleaf2
2. **Make changes**: Implement new features or fixes in the forked library
3. **Install this integration**: Install this custom component in Home Assistant
4. **Test**: Home Assistant will automatically pull the forked library
5. **Iterate**: Make changes to the fork and restart Home Assistant to test
6. **Submit PR**: Once satisfied, submit PRs to upstream projects:
   - Library changes → https://github.com/loebi-ch/aionanoleaf2
   - Integration changes (if any) → https://github.com/home-assistant/core

## Development Tips

### Local Development

For rapid iteration, you can:

1. Clone the aionanoleaf fork locally
2. Install it in development mode:
   ```bash
   cd /path/to/aionanoleaf
   pip install -e .
   ```
3. Restart Home Assistant to test changes

### Debugging

Enable debug logging in Home Assistant's `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.nanoleaf: debug
    aionanoleaf: debug
```

### Updating from Upstream

To update when the official integration changes:

1. Copy new files from Home Assistant core:
   ```bash
   git clone --depth 1 --filter=blob:none --sparse https://github.com/home-assistant/core.git
   cd core
   git sparse-checkout set homeassistant/components/nanoleaf
   ```

2. Copy files to this repository:
   ```bash
   cp homeassistant/components/nanoleaf/* /path/to/ha-nanoleaf/custom_components/nanoleaf/
   ```

3. Re-apply the manifest.json changes (requirements, codeowners, documentation, version)

4. Test and commit

## Integration Features

This integration supports all features from the official Nanoleaf integration:

### Platforms
- **Light**: Main platform for controlling Nanoleaf lights
- **Button**: Identify button for locating devices
- **Event**: Touch events for supported models

### Discovery
- **SSDP**: Automatic discovery via SSDP
- **Zeroconf**: Automatic discovery via mDNS/Zeroconf

### Models Supported
- NL29 (Aurora)
- NL42 (Canvas)
- NL47 (Shapes Triangles)
- NL48 (Shapes Mini Triangles)
- NL52 (Shapes Hexagons)
- NL59 (Lines)
- NL69 (Elements Hexagons)
- NL81 (Skylight)

### Features
- On/Off control
- Brightness adjustment
- Color control (RGB)
- Color temperature
- Effects selection
- Scene selection
- Touch gesture events (on supported models)
- Local push updates (no polling)

## Contributing

If you're working on this project:

1. Make changes to the aionanoleaf fork first
2. Test using this custom component
3. Document changes in CHANGELOG.md
4. Update version in manifest.json
5. Create pull requests to upstream once tested

## Links

- **This Repository**: https://github.com/latetedemelon/ha-nanoleaf
- **Forked Library**: https://github.com/latetedemelon/aionanoleaf2
- **Upstream Library**: https://github.com/loebi-ch/aionanoleaf2 (previously https://github.com/milanmeu/aionanoleaf, which Home Assistant dropped in 2026.3)
- **HA Core Integration**: https://github.com/home-assistant/core/tree/dev/homeassistant/components/nanoleaf
- **HA Documentation**: https://www.home-assistant.io/integrations/nanoleaf
