"""
Device management utilities for Tuya smart devices.
"""

import tinytuya
import os
import sys
import json
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
