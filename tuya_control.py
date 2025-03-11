#!/usr/bin/env python3
"""
Tuya Smart Bulb Control Script

This script allows you to control Tuya smart bulbs by turning them on or off,
and adjusting brightness, color temperature, and color.

Installation:
    pip install tinytuya

Usage:
    python tuya_control.py <bulb_name> <command> [value]
    python tuya_control.py all_bulbs <command> [value]  # Control all bulbs at once

Commands:
    on                      - Turn bulb on
    off                     - Turn bulb off
    status                  - Get current status
    brightness <level>      - Set brightness (10-1000)
    temperature <level>     - Set color temperature (0-1000, warm to cool)
    color <r> <g> <b>       - Set color using RGB values (0-255 each)

Examples:
    python tuya_control.py top on
    python tuya_control.py middle brightness 500
    python tuya_control.py bottom temperature 800
    python tuya_control.py top color 255 0 0      # Red color
    python tuya_control.py middle status
    python tuya_control.py all_bulbs off          # Turn off all bulbs
"""

import sys
import os
from utils.device_manager import setup_devices, connect_device
from commands.actions import perform_action


def print_usage():
    """Print usage instructions"""
    print(
        """
Usage: python tuya_control.py <bulb_name> <command> [value]
       python tuya_control.py all_bulbs <command> [value]  # Control all bulbs at once

Commands:
    on                      - Turn bulb on
    off                     - Turn bulb off
    status                  - Get current status
    brightness <level>      - Set brightness (10-1000)
    temperature <level>     - Set color temperature (0-1000, warm to cool)
    color <r> <g> <b>       - Set color using RGB values (0-255 each)
    """
    )


def main():
    # Check if devices.json exists
    if not os.path.exists("devices.json"):
        print("Error: devices.json not found.")
        print(
            "Please run 'python -m tinytuya wizard' to generate the required configuration files."
        )
        return

    # Get devices configuration
    device_configs = setup_devices()

    if len(sys.argv) < 3:
        print_usage()
        print(f"Available bulbs: {', '.join(device_configs.keys())}, all_bulbs")
        return

    bulb_name = sys.argv[1].lower()
    action = sys.argv[2].lower()

    # Handle the special case of controlling all bulbs
    if bulb_name == "all_bulbs":
        for name, config in device_configs.items():
            print(f"\nControlling bulb: {name}")
            bulb = connect_device(config)
            perform_action(bulb, action, sys.argv[3:])
        return

    if bulb_name not in device_configs:
        print(f"Unknown bulb name: {bulb_name}")
        print(f"Available bulbs: {', '.join(device_configs.keys())}, all_bulbs")
        return

    # Connect to the bulb
    config = device_configs[bulb_name]
    bulb = connect_device(config)

    # Perform the requested action
    perform_action(bulb, action, sys.argv[3:])


if __name__ == "__main__":
    main()
