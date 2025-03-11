#!/usr/bin/env python3
"""
Disco Mode for Tuya Smart Bulbs

This program creates a disco-like effect with rapid color changes on your Tuya smart bulbs.
It can target a specific bulb or all bulbs.

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
    """Generate vibrant RGB values for disco effect"""
    # Use more vibrant colors by making at least one value high
    color_type = random.randint(1, 6)

    if color_type == 1:  # Red dominant
        return 255, random.randint(0, 100), random.randint(0, 100)
    elif color_type == 2:  # Green dominant
        return random.randint(0, 100), 255, random.randint(0, 100)
    elif color_type == 3:  # Blue dominant
        return random.randint(0, 100), random.randint(0, 100), 255
    elif color_type == 4:  # Yellow
        return 255, 255, random.randint(0, 100)
    elif color_type == 5:  # Magenta
        return 255, random.randint(0, 100), 255
    else:  # Cyan
        return random.randint(0, 100), 255, 255


def main():
    # Register signal handler for clean exit with Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Get devices configuration
    device_configs = setup_devices()

    # Default values
    bulb_name = "all_bulbs"  # Default to all bulbs
    duration = 30  # Default to 30 seconds

    # Parse command line arguments
    if len(sys.argv) > 1:
        bulb_name = sys.argv[1].lower()

    if len(sys.argv) > 2:
        try:
            duration = int(sys.argv[2])
        except ValueError:
            print(f"Invalid duration: {sys.argv[2]}. Using default: 30 seconds.")
            duration = 30

    # Validate bulb name
    if bulb_name != "all_bulbs" and bulb_name not in device_configs:
        print(f"Unknown bulb name: {bulb_name}")
        print(f"Available bulbs: {', '.join(device_configs.keys())}, all_bulbs")
        return

    # Configure bulbs
    bulbs = {}
    if bulb_name == "all_bulbs":
        print("Setting up all bulbs for disco mode...")
        for name, config in device_configs.items():
            bulb = connect_device(config)
            turn_on_bulb(bulb)
            bulbs[name] = bulb
    else:
        print(f"Setting up {bulb_name} for disco mode...")
        bulb = connect_device(device_configs[bulb_name])
        turn_on_bulb(bulb)
        bulbs[bulb_name] = bulb

    # Track start time
    start_time = time.time()
    change_interval = 0.3  # Very quick changes for disco effect

    # Main program loop
    try:
        print(f"Starting disco mode for {duration} seconds. Press Ctrl+C to exit.")
        print("Hold on to your eyes! It's about to get flashy...")

        cycle_count = 0
        while running and (time.time() - start_time) < duration:
            cycle_count += 1

            # Generate new color
            r, g, b = generate_vibrant_color()

            # Apply to all configured bulbs
            for name, bulb in bulbs.items():
                set_color(bulb, r, g, b)

            # Brief status update every 10 cycles
            if cycle_count % 10 == 0:
                elapsed = time.time() - start_time
                remaining = max(0, duration - elapsed)
                print(f"Disco cycle {cycle_count}, {remaining:.1f} seconds remaining")

            # Quick delay for next color
            time.sleep(change_interval)

    except Exception as e:
        print(f"Error: {e}")

    print("Disco mode ended. Your lights have had quite the workout!")


if __name__ == "__main__":
    main()
