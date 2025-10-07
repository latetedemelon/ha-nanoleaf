# ha-nanoleaf
Patch for Nanoleaf integration to utilize new functionality under my fork of aionanoleaf

## Description

This is a custom component for Home Assistant that patches the official Nanoleaf integration to use a custom fork of the `aionanoleaf` library. This allows testing new features and improvements before they are submitted as pull requests to the upstream projects.

## Installation

### Manual Installation

1. Copy the `custom_components/nanoleaf` directory to your Home Assistant configuration directory:
   ```bash
   mkdir -p config/custom_components
   cp -r custom_components/nanoleaf config/custom_components/
   ```

2. Restart Home Assistant

3. The custom component will now use the forked `aionanoleaf` library from https://github.com/latetedemelon/aionanoleaf

### HACS Installation (Coming Soon)

This integration can be installed via HACS as a custom repository:

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add the URL: `https://github.com/latetedemelon/ha-nanoleaf`
6. Select category: "Integration"
7. Click "Add"
8. Find "Nanoleaf" in the list and click "Install"
9. Restart Home Assistant

## Usage

After installation, the custom component works exactly like the official Nanoleaf integration, but with any new features or fixes from the forked `aionanoleaf` library.

To configure:
1. Go to Settings → Devices & Services
2. Click "+ ADD INTEGRATION"
3. Search for "Nanoleaf"
4. Follow the configuration steps

## Development

This component is based on the Home Assistant core Nanoleaf integration and has been modified to use:
- Custom `aionanoleaf` library: https://github.com/latetedemelon/aionanoleaf

Any changes to the library will be automatically used when Home Assistant restarts.

## Contributing

If you find issues or have improvements, please open an issue or pull request on this repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

