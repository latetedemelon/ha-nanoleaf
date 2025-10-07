# Installation Guide

## Prerequisites

- Home Assistant instance (version 2024.1.0 or newer)
- Access to your Home Assistant configuration directory
- A Nanoleaf device on your network

## Method 1: Manual Installation

1. **Navigate to your Home Assistant configuration directory**
   
   This is typically `/config` in your Home Assistant installation, or `~/.homeassistant` if running in a virtual environment.

2. **Create the custom components directory** (if it doesn't exist)
   ```bash
   mkdir -p custom_components
   ```

3. **Copy the integration files**
   
   Copy the entire `custom_components/nanoleaf` directory from this repository to your Home Assistant `config/custom_components/` directory:
   ```bash
   cp -r custom_components/nanoleaf /path/to/homeassistant/config/custom_components/
   ```

4. **Restart Home Assistant**
   
   After copying the files, restart Home Assistant completely. This will:
   - Load the custom component
   - Download and install the custom `aionanoleaf` library from the forked repository

5. **Configure the integration**
   
   - Navigate to Settings → Devices & Services
   - Click "+ ADD INTEGRATION"
   - Search for "Nanoleaf"
   - Follow the on-screen instructions to set up your Nanoleaf device

## Method 2: HACS Installation (Recommended for easy updates)

1. **Add custom repository to HACS**
   
   - Open HACS in your Home Assistant
   - Click on "Integrations"
   - Click the three dots menu in the top right
   - Select "Custom repositories"
   - Add this repository URL: `https://github.com/latetedemelon/ha-nanoleaf`
   - Select category: "Integration"
   - Click "Add"

2. **Install the integration**
   
   - Search for "Nanoleaf" in HACS
   - Click "Download"
   - Restart Home Assistant

3. **Configure the integration**
   
   - Navigate to Settings → Devices & Services
   - Click "+ ADD INTEGRATION"
   - Search for "Nanoleaf"
   - Follow the on-screen instructions

## Verification

To verify the custom component is loaded correctly:

1. Check the Home Assistant logs for any errors related to `nanoleaf` or `aionanoleaf`
2. Look for messages indicating the custom `aionanoleaf` library was installed from GitHub
3. The integration should appear in Settings → Devices & Services

## Troubleshooting

### Component not loading

- Verify the directory structure is correct: `config/custom_components/nanoleaf/`
- Check that all files were copied correctly
- Restart Home Assistant and check the logs

### Library installation issues

If the custom `aionanoleaf` library fails to install:

1. Check your internet connection
2. Ensure your Home Assistant has permission to install packages
3. Check the Home Assistant logs for specific error messages
4. Try manually installing the library: `pip install git+https://github.com/latetedemelon/aionanoleaf.git`

### Conflicts with existing Nanoleaf integration

If you have the standard Nanoleaf integration installed:

1. Remove the standard integration from Settings → Devices & Services
2. Restart Home Assistant
3. Add the custom integration

## Updating

### Manual Installation

1. Delete the existing `custom_components/nanoleaf` directory
2. Copy the new version from this repository
3. Restart Home Assistant

### HACS Installation

1. Open HACS
2. Find the Nanoleaf integration
3. Click "Update" if available
4. Restart Home Assistant

## Uninstallation

1. Remove the integration from Settings → Devices & Services
2. Delete the `custom_components/nanoleaf` directory
3. Restart Home Assistant
4. (Optional) The standard Home Assistant Nanoleaf integration will become available again
