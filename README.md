# Tuya Smart Home

A simple Python package for controlling Tuya smart devices, primarily focused on smart bulbs.

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Device Configuration

Before using this package, you need to generate the required configuration files using the tinytuya wizard:

1. Run the tinytuya wizard command:
   ```
   python -m tinytuya wizard
   ```
2. Follow the prompts to:
   - Enter your Tuya IoT Platform credentials when asked
   - Connect to your Tuya IoT Platform account
   - Discover your devices
   - Scan your network to find device IP addresses
   
This wizard will generate several important configuration files:
- `devices.json` - Contains your device information including IDs and keys
- `snapshot.json` - Current state of your devices
- `tuya-raw.json` - Raw API response data
- `tinytuya.json` - Configuration for the tinytuya library

These files are required for the application to function properly.

## Usage

### Basic Control

```bash
# Turn on a bulb
python tuya_control.py top on

# Set brightness
python tuya_control.py middle brightness 500

# Set color temperature (warm to cool, 0-1000)
python tuya_control.py bottom temperature 800

# Set RGB color
python tuya_control.py top color 255 0 0  # Red

# Get device status
python tuya_control.py middle status

# Turn off all bulbs
python tuya_control.py all_bulbs off
```

### Light Effect Programs

The `programs/` directory contains scripts for various light effects:

```bash
# Random colors changing every 3 seconds
python programs/random_colors.py top 3

# Disco mode for 30 seconds
python programs/disco_mode.py all_bulbs 30

# Smooth color transitions for 15 minutes
python programs/color_fade.py middle 15
```

See the [programs README](programs/README.md) for more details on available light effects.

## Package Structure

- `tuya_control.py` - Main entry point
- `utils/`
  - `device_manager.py` - Functions for managing device connections
- `commands/`
  - `bulb_commands.py` - Functions for controlling bulbs
  - `actions.py` - Action handlers that connect commands to the main program
- `programs/`
  - Various programs for light effects and automation

## Requirements

- Python 3.6+
- tinytuya