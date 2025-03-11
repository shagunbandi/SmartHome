"""
Device management utilities for Tuya smart devices.
"""

import tinytuya
import os
import sys
import json


def setup_devices():
    """Load the Tuya devices from devices.json"""
    devices = {}

    try:
        # Try to load devices from devices.json file
        if not os.path.exists("devices.json"):
            print("Error: devices.json file not found.")
            print(
                "Please run 'python -m tinytuya wizard' to generate the required configuration files."
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
            print("Please run 'python -m tinytuya wizard' to discover your devices.")
            sys.exit(1)

        print(f"Loaded {len(devices)} devices from devices.json.")
        return devices

    except Exception as e:
        print(f"Error loading devices from devices.json: {e}")
        print(
            "Please run 'python -m tinytuya wizard' to generate the required configuration files."
        )
        sys.exit(1)


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
