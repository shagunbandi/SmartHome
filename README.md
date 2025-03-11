# Tuya Smart Bulb Controller

A Python script to control Tuya smart bulbs via local network.

## Features

- Turn bulbs on/off
- Set brightness levels
- Adjust color temperature
- Set RGB colors
- Get current bulb status
- Control multiple bulbs simultaneously

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Set up your device configuration:

Option A: Use the TinyTuya wizard to automatically discover and configure your devices:
```bash
pip install tinytuya
tinytuya wizard
```

Option B: Create the `devices.json` file manually with the following structure:
```json
[
  {
    "name": "Living Room",
    "id": "your_device_id",
    "key": "your_local_key",
    "ip": "192.168.1.x"
  },
  {
    "name": "Bedroom",
    "id": "your_device_id",
    "key": "your_local_key",
    "ip": "192.168.1.x"
  }
]
```

## Usage

The script provides a simple command-line interface:

```bash
python tuya_control.py <bulb_name> <command> [value]
```

Or to control all bulbs at once:

```bash
python tuya_control.py all_bulbs <command> [value]
```

### Available Commands

- `on` - Turn the bulb on
- `off` - Turn the bulb off
- `status` - Display current bulb settings
- `brightness <level>` - Set brightness (10-1000)
- `temperature <level>` - Set color temperature (0-1000)
- `color <r> <g> <b>` - Set color (RGB values 0-255)

### Examples

```bash
# Turn on the living room bulb
python tuya_control.py living_room on

# Set bedroom bulb to 50% brightness
python tuya_control.py bedroom brightness 500

# Set kitchen bulb to cool white
python tuya_control.py kitchen temperature 800

# Set dining room bulb to red
python tuya_control.py dining_room color 255 0 0

# Turn off all bulbs
python tuya_control.py all_bulbs off
```

## Troubleshooting

If you encounter issues with colors not setting correctly, try these steps:

1. Make sure your bulbs are using the correct version (default is 3.5)
2. Ensure your local network allows the necessary traffic
3. Check the device IP addresses are current and reachable
4. Run the status command to see the raw data from the device
5. Make sure no other app (like the Smart Life app) is controlling the device at the same time

## Getting Device Keys

If you need to find your device keys manually:

1. Install the Smart Life or Tuya Smart app and connect your devices
2. Create a Tuya IoT Developer account at iot.tuya.com
3. Create a cloud project and link your app account
4. Use the TinyTuya wizard to extract the local keys

```bash
tinytuya wizard
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

```markdown
# Obtaining API Key and Secret from Tuya

1. Go to the [Tuya Developer Platform](https://developer.tuya.com/en/)
2. Sign in with your Tuya account.
3. Click on "Cloud" in the top navigation bar.
4. Under "Cloud Development", click on "API Explorer".
5. Click on "Create" to create a new project.
6. Fill in the required information and click on "Create".
7. Once the project is created, click on the project name to view the details.
8. Under "API Key", you will find your API Key.
9. Click on "Show" to reveal your Secret.
10. Make sure to copy both your API Key and Secret and keep them secure.

That's it! You have now obtained your API Key and Secret from Tuya.
```

# Smart Home Light Control

This repository contains scripts to control Tuya-based smart lights using the TinyTuya library.

## Setup

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Ensure your `devices.json` file is correctly set up with your device information.

## Available Scripts

### Blink Lights Script

The `blink_lights.py` script will blink each of your smart bulbs 3 times.

To run the script:
```
python blink_lights.py
```

This script will:
1. Connect to each light in your devices.json file
2. Blink each light OFF and ON three times
3. Return the light to its original state

### Diagnostic Tool

The `test_bulb.py` script provides a comprehensive diagnostic tool to troubleshoot connection issues with your smart bulbs.

To run the diagnostic tool:
```
python test_bulb.py
```

This interactive script will:
1. Show a list of your devices from devices.json
2. Let you select which device to test
3. Perform a series of connectivity tests:
   - Network ping test
   - TinyTuya device detection
   - Device status retrieval
   - Optional light toggle test
4. Provide detailed feedback and troubleshooting recommendations

You can also directly test a specific device by ID:
```
python test_bulb.py DEVICE_ID
```

## Troubleshooting

If you encounter connection issues:
- Make sure your computer is on the same network as your smart bulbs
- Verify the IP addresses in devices.json are current
- Check that your local_key values are correct

If the script can't control your devices, you may need to run the TinyTuya wizard to refresh your device information:
```
python -m tinytuya wizard
```

### Finding Current IP Addresses

IP addresses of your devices may change over time. To find the current IP addresses:
```
python -m tinytuya scan
```

Then update your devices.json file with the new IP addresses.

