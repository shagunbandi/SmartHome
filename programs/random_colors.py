#!/usr/bin/env python3
"""
Random Colors Program for Tuya Smart Bulbs

This program changes bulb colors randomly at set intervals.

Usage:
    python programs/random_colors.py [bulb_name] [interval_seconds]
    python programs/random_colors.py all_bulbs [interval_seconds]

Examples:
    python programs/random_colors.py top 2         # Change top bulb every 2 seconds
    python programs/random_colors.py all_bulbs 5   # Change all bulbs every 5 seconds
"""

import sys
import time
import random
import os
import signal
import threading

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.device_manager import setup_devices, connect_device
from commands.bulb_commands import set_color, turn_on_bulb

# Global variable to track if the program should keep running
running = True


def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully exit"""
    global running
    print("\nStopping random colors. Exiting...")
    running = False


def generate_random_color():
    """Generate random RGB values"""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b


def run_program(device, duration=300, interval=3, stop_event=None):
    """
    Run the random colors program on a device or list of devices

    Args:
        device: A single bulb device or list of devices
        duration: Duration in seconds (default 5 minutes)
        interval: Seconds between color changes (default 3 seconds)
        stop_event: Optional threading.Event to signal when to stop
    """
    # Handle either single device or list of devices
    devices = [device] if not isinstance(device, list) else device

    # Turn on all bulbs
    for device in devices:
        turn_on_bulb(device)

    print(
        f"Starting random colors for {duration} seconds, changing every {interval} seconds..."
    )

    # Calculate end time
    start_time = time.time()
    end_time = start_time + duration

    try:
        # Count color changes
        change_count = 0

        # Keep running until duration ends or stopped
        while time.time() < end_time and (
            stop_event is None or not stop_event.is_set()
        ):

            # Generate a random color
            r, g, b = generate_random_color()

            # Apply to all devices
            for device in devices:
                set_color(device, r, g, b)

            # Increment counter
            change_count += 1

            # Display status
            time_left = int(end_time - time.time())
            print(
                f"Color change #{change_count}: RGB({r},{g},{b}), {time_left} seconds remaining"
            )

            # Calculate time to wait
            wait_time = interval
            if time.time() + wait_time > end_time:
                wait_time = max(0, end_time - time.time())

            # Wait for the interval or until stopped
            if stop_event:
                # Check stop_event every 0.5 seconds instead of blocking for the full interval
                for _ in range(int(wait_time * 2)):
                    if stop_event.is_set():
                        break
                    time.sleep(0.5)
            else:
                time.sleep(wait_time)

    except Exception as e:
        print(f"Error in random colors: {e}")

    print("Random colors program completed")


def main():
    # Register signal handler for clean exit with Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python random_colors.py [bulb_name] [interval_seconds]")
        return

    bulb_name = sys.argv[1].lower()

    # Default interval 3 seconds if not specified
    interval_seconds = 3
    if len(sys.argv) > 2:
        try:
            interval_seconds = int(sys.argv[2])
            # Ensure reasonable interval range
            interval_seconds = max(1, min(30, interval_seconds))
        except ValueError:
            print(f"Invalid interval: {sys.argv[2]}. Using default (3 seconds).")

    # Default duration 5 minutes
    duration_seconds = 300

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
        run_program(devices, duration=duration_seconds, interval=interval_seconds)
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
    run_program(device, duration=duration_seconds, interval=interval_seconds)


if __name__ == "__main__":
    main()
