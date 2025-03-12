#!/usr/bin/env python3
"""
Disco Mode Program for Tuya Smart Bulbs

This program creates a disco-like effect with rapid color changes, focusing on vibrant colors.

Usage:
    python programs/disco_mode.py [bulb_name] [duration_seconds]
    python programs/disco_mode.py all_bulbs [duration_seconds]

Examples:
    python programs/disco_mode.py top 30        # Disco mode on top bulb for 30 seconds
    python programs/disco_mode.py all_bulbs 60  # Disco mode on all bulbs for 60 seconds
"""

import sys
import time
import random
import os
import signal
import threading
import traceback

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.device_manager import setup_devices, connect_device
from commands.bulb_commands import set_color, turn_on_bulb

# Global variable to track if the program should keep running
running = True


def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully exit"""
    global running
    print("\nStopping disco mode. Exiting...")
    running = False


def generate_vibrant_color():
    """Generate vibrant RGB values for a disco effect"""
    # Generate at least one color channel with high intensity
    # and make the other channels more random
    primary = random.randint(0, 2)  # 0=R, 1=G, 2=B

    r = random.randint(180, 255) if primary == 0 else random.randint(0, 100)
    g = random.randint(180, 255) if primary == 1 else random.randint(0, 100)
    b = random.randint(180, 255) if primary == 2 else random.randint(0, 100)

    return r, g, b


def run_program(device, duration=60, stop_event=None, interval=0.3):
    """
    Run the disco mode program on a device or list of devices

    Args:
        device: A single bulb device or list of devices
        duration: Duration in seconds (default 60 seconds)
        stop_event: Optional threading.Event to signal when to stop
        interval: Time between color changes in seconds (default 0.3)
    """
    print(
        f"Starting disco mode with parameters: duration={duration}, stop_event={stop_event is not None}"
    )

    try:
        # Handle either single device or list of devices
        devices = [device] if not isinstance(device, list) else device

        # Print device info
        print(f"Running disco mode on {len(devices)} device(s)")

        # Settings
        color_change_interval = interval  # seconds between color changes

        # Turn on all bulbs
        for device in devices:
            try:
                turn_on_bulb(device)
            except Exception as e:
                print(f"Error turning on device: {e}")
                traceback.print_exc()

        print(f"Starting disco mode for {duration} seconds...")

        # Calculate end time
        start_time = time.time()
        end_time = start_time + duration

        # Keep running until duration ends or stopped
        while time.time() < end_time and (
            stop_event is None or not stop_event.is_set()
        ):
            # Generate a vibrant color
            r, g, b = generate_vibrant_color()
            print(f"Disco color: RGB({r}, {g}, {b})")

            # Apply to all devices
            for device in devices:
                try:
                    # Make sure we're passing proper integer values
                    set_color(device, int(r), int(g), int(b))
                except Exception as e:
                    print(f"Error setting color: {e}")
                    traceback.print_exc()

            # Sleep for the interval
            time.sleep(color_change_interval)

            # Display remaining time every few color changes
            if random.randint(1, 10) == 1:
                remaining = end_time - time.time()
                print(f"Disco mode: {int(remaining)} seconds remaining")

    except Exception as e:
        print(f"Error in disco mode: {e}")
        traceback.print_exc()

    print("Disco mode program completed")


def main():
    # Register signal handler for clean exit with Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python disco_mode.py [bulb_name] [duration_seconds]")
        return

    bulb_name = sys.argv[1].lower()

    # Default duration 30 seconds if not specified
    duration_seconds = 30
    if len(sys.argv) > 2:
        try:
            duration_seconds = int(sys.argv[2])
        except ValueError:
            print(f"Invalid duration: {sys.argv[2]}. Using default (30 seconds).")

    # Get devices configuration
    device_configs = setup_devices()

    # Handle the special case of controlling all bulbs
    if bulb_name == "all_bulbs":
        devices = []
        for name, config in device_configs.items():
            print(f"Adding bulb: {name}")
            device = connect_device(config)
            devices.append(device)

        if not devices:
            print("No bulbs found.")
            return

        # Call run_program with the list of devices
        run_program(devices, duration=duration_seconds)
        return

    # Handle single bulb
    if bulb_name not in device_configs:
        print(f"Unknown bulb name: {bulb_name}")
        print(f"Available bulbs: {', '.join(device_configs.keys())}, all_bulbs")
        return

    # Connect to the bulb
    config = device_configs[bulb_name]
    device = connect_device(config)

    # Run the program
    run_program(device, duration=duration_seconds)


if __name__ == "__main__":
    main()
