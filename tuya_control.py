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

import tinytuya
import time
import sys
import json
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Get API credentials from environment variables
TUYA_API_KEY = os.getenv("TUYA_API_KEY")
TUYA_API_SECRET = os.getenv("TUYA_API_SECRET")
TUYA_REGION = os.getenv("TUYA_REGION", "eu")  # Default to EU region if not specified


def setup_devices():
    """Load the Tuya devices from devices.json"""
    devices = {}

    try:
        # Try to load devices from devices.json file
        if not os.path.exists("devices.json"):
            print("Error: devices.json file not found.")
            print(
                "Please run 'tinytuya wizard' or create a devices.json file manually."
            )
            sys.exit(1)

        with open("devices.json", "r") as f:
            devices_data = json.load(f)

        # Format the data from devices.json
        for device in devices_data:
            # Skip non-bulb devices if any
            if "category" in device and device["category"] != "dj":
                continue

            # Use name as the key (lowercase for consistency)
            name = device["name"].lower()

            # Create entry with necessary device info
            devices[name] = {
                "device_id": device["id"],
                "ip_address": device.get("ip"),  # Use IP if available
                "local_key": device["key"],
                "version": device.get(
                    "version", "3.5"
                ),  # Use version if available, default to 3.5
            }

        if not devices:
            print("Error: No bulb devices found in devices.json.")
            print(
                "Please run 'tinytuya wizard' or add devices to devices.json manually."
            )
            sys.exit(1)

        print(f"Loaded {len(devices)} devices from devices.json.")
        return devices

    except Exception as e:
        print(f"Error loading devices from devices.json: {e}")
        print("Please run 'tinytuya wizard' or create a devices.json file manually.")
        sys.exit(1)


def create_or_update_devices_json():
    """Create or update devices.json using API credentials"""
    if not TUYA_API_KEY or not TUYA_API_SECRET:
        print(
            "Environment variables TUYA_API_KEY and TUYA_API_SECRET must be set to run the wizard"
        )
        print("Please set them in the .env file and try again")
        return False

    try:
        # Initialize Tuya Cloud connection
        cloud = tinytuya.Cloud(
            apiRegion=TUYA_REGION,
            apiKey=TUYA_API_KEY,
            apiSecret=TUYA_API_SECRET,
            apiDeviceID="tuya_control_script",
        )

        # Get devices
        print("Connecting to Tuya Cloud API...")
        devices = cloud.getdevices()

        if not devices:
            print("No devices found. Please check your API credentials.")
            return False

        print(f"Found {len(devices)} devices in the Tuya Cloud")

        # Create a list for devices.json
        device_list = []
        for device in devices:
            device_info = {
                "name": device.get("name", "Unknown"),
                "id": device.get("id", ""),
                "key": device.get("local_key", ""),
                "ip": "",  # IP will be filled in later
                "product_name": device.get("product_name", ""),
                "category": device.get("category", ""),
                "version": "3.5",  # Default version
            }
            device_list.append(device_info)

        # Save to devices.json
        with open("devices.json", "w") as f:
            json.dump(device_list, f, indent=2)

        print(f"Saved {len(device_list)} devices to devices.json")

        # Run the scan to fill in IP addresses
        print("\nScanning for device IP addresses...")
        os.system("python -m tinytuya scan")

        return True
    except Exception as e:
        print(f"Error connecting to Tuya Cloud: {e}")
        return False


def connect_device(config):
    """Connect to a Tuya bulb device

    Args:
        config: Device configuration with device_id, ip_address, and local_key

    Returns:
        Connected BulbDevice object
    """
    device = tinytuya.BulbDevice(
        dev_id=config["device_id"],
        address=config["ip_address"],
        local_key=config["local_key"],
        version=config.get(
            "version", "3.5"
        ),  # Use the device's version or default to 3.5
    )

    # Set the bulb to use persistent connections
    device.set_socketPersistent(True)

    return device


def turn_on_bulb(device):
    """Turn on a Tuya bulb"""
    try:
        result = device.turn_on()
        print(f"Bulb turned ON")
        return True
    except Exception as e:
        print(f"Error turning bulb ON: {e}")
        return False


def turn_off_bulb(device):
    """Turn off a Tuya bulb"""
    try:
        result = device.turn_off()
        print(f"Bulb turned OFF")
        return True
    except Exception as e:
        print(f"Error turning bulb OFF: {e}")
        return False


def set_brightness(device, brightness):
    """Set the brightness of a Tuya bulb

    Args:
        device: The connected bulb device
        brightness: Integer value between 10-1000
    """
    try:
        # Ensure brightness is within valid range
        brightness = max(10, min(1000, int(brightness)))

        # Use the built-in method to set brightness
        result = device.set_brightness(brightness)
        print(f"Brightness set to {brightness}")
        return True
    except Exception as e:
        print(f"Error setting brightness: {e}")
        return False


def set_temperature(device, temperature):
    """Set the color temperature of a Tuya bulb

    Args:
        device: The connected bulb device
        temperature: Integer value between 0-1000 (warm to cool)
    """
    try:
        # Ensure temperature is within valid range
        temperature = max(0, min(1000, int(temperature)))

        # Use the built-in method to set white temperature
        # First parameter is brightness (using max), second is temperature
        result = device.set_white(1000, temperature)
        print(f"Color temperature set to {temperature}")
        return True
    except Exception as e:
        print(f"Error setting color temperature: {e}")
        return False


def set_color(device, r, g, b):
    """Set the color of a Tuya bulb using RGB values

    Args:
        device: The connected bulb device
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)
    """
    try:
        # Ensure RGB values are within valid ranges
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))

        # Use the built-in method to set color
        result = device.set_colour(r, g, b)

        # Check if set_colour succeeded
        if isinstance(result, dict) and "Error" in result:
            print(f"Failed to set color: {result['Error']}")

            # Try alternative approach if built-in method fails
            print("Trying alternative color setting method...")

            # First set mode to 'colour'
            device.set_value(21, "colour")

            # Convert RGB to HSV
            from colorsys import rgb_to_hsv

            h, s, v = rgb_to_hsv(r / 255, g / 255, b / 255)

            # Format according to Tuya expectations
            hsv = {"h": int(h * 360), "s": int(s * 1000), "v": int(v * 1000)}

            # Try setting color_data_v2 (DPS 24) with JSON
            hsv_json = json.dumps(hsv)
            result = device.set_value(24, hsv_json)

            if result and "Error" not in result:
                print(f"Color set to RGB({r}, {g}, {b}) using HSV JSON format")
                return True
            else:
                # One last attempt using HSV hex format
                h_value = int(h * 360)
                s_value = int(s * 1000)
                v_value = int(v * 1000)
                hsv_hex = f"{h_value:04x}{s_value:04x}{v_value:04x}"
                result = device.set_value(24, hsv_hex)

                if result and "Error" not in result:
                    print(f"Color set to RGB({r}, {g}, {b}) using HSV hex format")
                    return True
                else:
                    print(f"All color setting methods failed: {result}")
                    return False
        else:
            print(f"Color set to RGB({r}, {g}, {b})")
            return True

    except Exception as e:
        print(f"Error setting color: {e}")
        return False


def get_status(device):
    """Get the current status of a Tuya bulb"""
    try:
        # Request status update
        data = device.status()
        if "dps" not in data:
            print("Error: No status data returned")
            return False

        dps = data["dps"]

        # Print the status in a user-friendly format
        print("\nCurrent bulb status:")
        print(f"Power: {'ON' if dps.get('20', False) else 'OFF'}")
        print(f"Mode: {dps.get('21', 'unknown')}")
        print(f"Brightness: {dps.get('22', 'unknown')}")
        print(f"Color Temperature: {dps.get('23', 'unknown')}")

        # Try to parse color data if available
        if "24" in dps:
            try:
                color_data = dps["24"]
                print(f"Color data (raw): {color_data}")

                # Try to parse as JSON
                if isinstance(color_data, str) and "{" in color_data:
                    try:
                        color_json = json.loads(color_data)
                        if (
                            "h" in color_json
                            and "s" in color_json
                            and "v" in color_json
                        ):
                            print(
                                f"Color (HSV): H:{color_json['h']} S:{color_json['s']} V:{color_json['v']}"
                            )
                    except:
                        pass

                # If it's a hex string, try to decode
                if isinstance(color_data, str) and len(color_data) >= 12:
                    try:
                        # Attempt to decode as HSV hex
                        if len(color_data) == 12:  # HSV format
                            h_hex = color_data[0:4]
                            s_hex = color_data[4:8]
                            v_hex = color_data[8:12]

                            h = int(h_hex, 16)
                            s = int(s_hex, 16)
                            v = int(v_hex, 16)

                            print(f"Color (HSV hex): H:{h} S:{s} V:{v}")
                    except Exception as e:
                        print(f"Error parsing hex color: {e}")
            except Exception as e:
                print(f"Error parsing color data: {e}")

        return True
    except Exception as e:
        print(f"Error getting status: {e}")
        return False


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
    # Check if devices.json exists, if not, try to create it
    if not os.path.exists("devices.json") and TUYA_API_KEY and TUYA_API_SECRET:
        print("devices.json not found. Attempting to create it...")
        if not create_or_update_devices_json():
            print("Could not create devices.json. Exiting.")
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


def perform_action(bulb, action, args):
    """Perform the requested action on a bulb

    Args:
        bulb: The connected bulb device
        action: The action to perform (on, off, etc.)
        args: Additional arguments for the action
    """
    if action == "on":
        turn_on_bulb(bulb)
    elif action == "off":
        turn_off_bulb(bulb)
    elif action == "status":
        get_status(bulb)
    elif action == "brightness":
        if not args:
            print("Error: Brightness value required (10-1000)")
            return
        set_brightness(bulb, args[0])
    elif action == "temperature":
        if not args:
            print("Error: Temperature value required (0-1000)")
            return
        set_temperature(bulb, args[0])
    elif action == "color":
        if len(args) < 3:
            print("Error: Color requires 3 values: <r> <g> <b>")
            print("RGB values should be between 0-255")
            return
        set_color(bulb, args[0], args[1], args[2])
    else:
        print(f"Unknown action: {action}")
        print_usage()


if __name__ == "__main__":
    main()
