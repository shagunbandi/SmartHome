#!/usr/bin/env python3
"""
Random Colors Program for Tuya Smart Bulbs

This program cycles through random colors on your Tuya smart bulbs.
It can target a specific bulb or all bulbs.

Usage:
    python programs/random_colors.py [bulb_name] [interval_seconds]
    python programs/random_colors.py all_bulbs [interval_seconds]

Examples:
    python programs/random_colors.py top 2        # Change top bulb every 2 seconds
    python programs/random_colors.py all_bulbs 5  # Change all bulbs every 5 seconds
"""

import sys
import time
import random
import os
import signal

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.device_manager import setup_devices, connect_device
from commands.bulb_commands import set_color, turn_on_bulb

# Global variable to track if the program should keep running
running = True


def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully exit"""
    global running
    print("\nStopping color changes. Exiting...")
    running = False


def generate_random_color():
    """Generate random RGB values"""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b


def main():
    # Register signal handler for clean exit with Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Get devices configuration
    device_configs = setup_devices()

    # Default values
    bulb_name = "all_bulbs"  # Default to all bulbs
    interval = 3  # Default to 3 seconds

    # Parse command line arguments
    if len(sys.argv) > 1:
        bulb_name = sys.argv[1].lower()

    if len(sys.argv) > 2:
        try:
            interval = float(sys.argv[2])
        except ValueError:
            print(f"Invalid interval: {sys.argv[2]}. Using default: 3 seconds.")
            interval = 3

    # Validate bulb name
    if bulb_name != "all_bulbs" and bulb_name not in device_configs:
        print(f"Unknown bulb name: {bulb_name}")
        print(f"Available bulbs: {', '.join(device_configs.keys())}, all_bulbs")
        return

    # Function to change a bulb to a random color
    def change_bulb_color(name, config):
        bulb = connect_device(config)

        # Make sure the bulb is on first
        turn_on_bulb(bulb)

        # Generate and set random color
        r, g, b = generate_random_color()
        print(f"Setting {name} to RGB({r}, {g}, {b})")
        set_color(bulb, r, g, b)

    # Main program loop
    try:
        print(f"Starting random color program. Press Ctrl+C to exit.")
        print(f"Changing colors every {interval} seconds...")

        cycle_count = 0
        while running:
            cycle_count += 1
            print(f"\nCycle {cycle_count}:")

            # Handle single bulb or all bulbs
            if bulb_name == "all_bulbs":
                for name, config in device_configs.items():
                    change_bulb_color(name, config)
            else:
                change_bulb_color(bulb_name, device_configs[bulb_name])

            # Wait for the specified interval
            time_remaining = interval
            while running and time_remaining > 0:
                time.sleep(
                    min(0.1, time_remaining)
                )  # Sleep in small increments for responsiveness
                time_remaining -= 0.1

    except Exception as e:
        print(f"Error: {e}")

    print("Random color program ended.")


if __name__ == "__main__":
    main()
