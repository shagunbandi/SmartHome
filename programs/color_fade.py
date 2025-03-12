#!/usr/bin/env python3
"""
Color Fade Program for Tuya Smart Bulbs

This program creates a smooth transition between colors on your Tuya smart bulbs.
It gradually fades between random colors for a relaxing effect.

Usage:
    python programs/color_fade.py [bulb_name] [duration_minutes]
    python programs/color_fade.py all_bulbs [duration_minutes]

Examples:
    python programs/color_fade.py top 10        # Color fade on top bulb for 10 minutes
    python programs/color_fade.py all_bulbs 30  # Color fade on all bulbs for 30 minutes
"""

import sys
import time
import random
import os
import signal
import math
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
    print("\nStopping color fade. Exiting...")
    running = False


def generate_soft_color():
    """Generate softer RGB values for relaxing transitions"""
    # Avoid harsh/bright colors for a calmer effect
    r = random.randint(50, 200)
    g = random.randint(50, 200)
    b = random.randint(50, 200)
    return r, g, b


def interpolate_color(color1, color2, step, total_steps):
    """Interpolate between two colors"""
    r1, g1, b1 = color1
    r2, g2, b2 = color2

    r = int(r1 + (r2 - r1) * step / total_steps)
    g = int(g1 + (g2 - g1) * step / total_steps)
    b = int(b1 + (b2 - b1) * step / total_steps)

    return r, g, b


# New function that can be called directly from the server
def run_program(device, duration=600, stop_event=None):
    """
    Run the color fade program on a device or list of devices

    Args:
        device: A single bulb device or list of devices
        duration: Duration in seconds (default 10 minutes)
        stop_event: Optional threading.Event to signal when to stop
    """
    # Handle either single device or list of devices
    devices = [device] if not isinstance(device, list) else device

    # Settings
    transition_time = 4  # Seconds per transition
    total_steps = 40  # Steps per transition
    step_time = transition_time / total_steps

    # Convert duration to transitions
    max_transitions = int(duration / transition_time)
    transitions_count = 0

    # Generate initial color
    current_color = generate_soft_color()

    # Turn on the bulbs
    for device in devices:
        turn_on_bulb(device)

    print(f"Starting color fade for {duration} seconds...")
    try:
        # Keep running until max transitions or until stopped
        while transitions_count < max_transitions and (
            stop_event is None or not stop_event.is_set()
        ):

            # Generate target color for this transition
            target_color = generate_soft_color()

            # Perform the transition in steps
            for step in range(total_steps + 1):
                # Check for stop event
                if stop_event and stop_event.is_set():
                    print("Received stop signal")
                    return

                # Calculate the interpolated color for this step
                interpolated_color = interpolate_color(
                    current_color, target_color, step, total_steps
                )

                # Apply the color to all devices
                for device in devices:
                    set_color(device, *interpolated_color)

                # Sleep for the step duration
                time.sleep(step_time)

            # The target color becomes our new current color
            current_color = target_color

            # Increment transition counter
            transitions_count += 1

            # Print progress
            print(f"Completed transition {transitions_count}/{max_transitions}")

    except Exception as e:
        print(f"Error in color fade: {e}")

    print("Color fade program completed")


def main():
    # Register signal handler for clean exit with Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python color_fade.py [bulb_name] [duration_minutes]")
        return

    bulb_name = sys.argv[1].lower()

    # Default duration 10 minutes if not specified
    duration_minutes = 10
    if len(sys.argv) > 2:
        try:
            duration_minutes = int(sys.argv[2])
        except ValueError:
            print(f"Invalid duration: {sys.argv[2]}. Using default (10 minutes).")

    # Convert minutes to seconds
    duration_seconds = duration_minutes * 60

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
