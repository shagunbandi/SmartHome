# Tuya Smart Home

A simple Python package for controlling Tuya smart devices, primarily focused on smart bulbs.

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install tinytuya python-dotenv
   ```
3. Create a `.env` file with your Tuya credentials:
   ```
   TUYA_API_KEY=your_api_key
   TUYA_API_SECRET=your_api_secret
   TUYA_REGION=eu  # or cn, us, etc.
   ```

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
- python-dotenv
