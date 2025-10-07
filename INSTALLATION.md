# Installation Guide for ha-nanoleaf

This guide will help you install the Nanoleaf custom component for Home Assistant.

## Prerequisites

- Home Assistant installed (version 2024.1.0 or later)
- Access to your Home Assistant configuration directory
- Network access to your Nanoleaf devices

## Method 1: Installation via HACS (Recommended)

### Step 1: Add Custom Repository

1. Open Home Assistant
2. Navigate to **HACS** (Home Assistant Community Store)
3. Click on **Integrations**
4. Click the **three dots** (⋮) in the top-right corner
5. Select **Custom repositories**
6. In the dialog that appears:
   - Repository: `https://github.com/latetedemelon/ha-nanoleaf`
   - Category: `Integration`
7. Click **Add**

### Step 2: Install the Integration

1. Search for "Nanoleaf" in the HACS Integrations list
2. Click on the **Nanoleaf** integration
3. Click **Download**
4. Restart Home Assistant

## Method 2: Manual Installation

### Step 1: Download the Component

1. Download the latest release from [GitHub](https://github.com/latetedemelon/ha-nanoleaf)
2. Extract the archive

### Step 2: Copy Files

1. Locate your Home Assistant configuration directory (usually `/config`)
2. Create a `custom_components` directory if it doesn't exist
3. Copy the entire `custom_components/nanoleaf` folder to your `custom_components` directory

Your directory structure should look like this:
```
config/
├── custom_components/
│   └── nanoleaf/
│       ├── __init__.py
│       ├── manifest.json
│       ├── light.py
│       └── ... (other files)
```

### Step 3: Restart Home Assistant

Restart Home Assistant to load the new component.

## Setting Up Your Nanoleaf Device

### Step 1: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION**
3. Search for **Nanoleaf**
4. Click on the Nanoleaf integration

### Step 2: Enter Device Information

1. Enter the IP address or hostname of your Nanoleaf device
   - You can find this in your router's DHCP list or the Nanoleaf app
   - Example: `192.168.1.100` or `nanoleaf-shapes.local`

### Step 3: Authorize the Connection

1. **Press and hold** the power button on your Nanoleaf device for **5 seconds**
   - The LEDs on the device will start flashing to indicate it's ready to pair
2. Within **30 seconds**, click **Submit** in Home Assistant
3. The integration will connect and configure your device

### Step 4: Enjoy Your Nanoleaf Device

Your Nanoleaf device is now integrated with Home Assistant! You should see:
- A light entity for controlling your panels
- An identify button for locating the device
- Touch event entities (for compatible models)

## Automatic Discovery

The integration supports automatic discovery. If your Nanoleaf device is on the same network, it may be automatically detected via:

- **SSDP** (Simple Service Discovery Protocol)
- **Zeroconf/mDNS** (Bonjour)
- **HomeKit** discovery

When discovered, you'll see a notification in Home Assistant. Click **Configure** and follow the authorization steps above.

## Troubleshooting

### Device Not Found

- Ensure your Nanoleaf device is powered on and connected to the network
- Check that your device is on the same network as Home Assistant
- Try using the IP address instead of the hostname
- Verify the device IP address hasn't changed (consider setting a static IP)

### Authorization Failed

- Make sure you press and hold the power button until the LEDs flash
- Complete the authorization within 30 seconds
- Try the process again if the window expires
- Ensure no other devices are trying to pair simultaneously

### Integration Not Loading

- Verify all files were copied correctly to the `custom_components/nanoleaf` directory
- Check Home Assistant logs for any error messages
- Ensure you're running Home Assistant 2024.1.0 or later
- Try restarting Home Assistant again

### Dependency Installation Issues

The integration uses a custom fork of aionanoleaf. If you encounter installation issues:

1. Check your Home Assistant logs for pip install errors
2. Ensure your Home Assistant has internet access
3. Try restarting Home Assistant to trigger a fresh install
4. Check GitHub to ensure the aionanoleaf fork repository is accessible

## Getting Help

If you encounter any issues:

1. Check the [GitHub Issues](https://github.com/latetedemelon/ha-nanoleaf/issues)
2. Review the Home Assistant logs for error messages
3. Open a new issue with:
   - Home Assistant version
   - Error logs
   - Steps to reproduce the problem

## Next Steps

After installation, explore:

- [Automation examples in the README](../README.md#touch-gesture-support)
- Setting up device triggers for touch gestures
- Creating scenes with your Nanoleaf effects
- Using the identify button to locate your device
