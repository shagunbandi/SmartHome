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
    """Create a smooth transition between two colors"""
    r1, g1, b1 = color1
    r2, g2, b2 = color2

    # Calculate interpolated color values
    r = int(r1 + (r2 - r1) * step / total_steps)
    g = int(g1 + (g2 - g1) * step / total_steps)
    b = int(b1 + (b2 - b1) * step / total_steps)

    return r, g, b


def main():
    # Register signal handler for clean exit with Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Get devices configuration
    device_configs = setup_devices()

    # Default values
    bulb_name = "all_bulbs"  # Default to all bulbs
    duration_minutes = 15  # Default to 15 minutes
    transition_time = 30  # Seconds to transition between colors

    # Parse command line arguments
    if len(sys.argv) > 1:
        bulb_name = sys.argv[1].lower()

    if len(sys.argv) > 2:
        try:
            duration_minutes = int(sys.argv[2])
        except ValueError:
            print(f"Invalid duration: {sys.argv[2]}. Using default: 15 minutes.")
            duration_minutes = 15

    # Validate bulb name
    if bulb_name != "all_bulbs" and bulb_name not in device_configs:
        print(f"Unknown bulb name: {bulb_name}")
        print(f"Available bulbs: {', '.join(device_configs.keys())}, all_bulbs")
        return

    # Configure bulbs
    bulbs = {}
    if bulb_name == "all_bulbs":
        print("Setting up all bulbs for color fade...")
        for name, config in device_configs.items():
            bulb = connect_device(config)
            turn_on_bulb(bulb)
            bulbs[name] = bulb
    else:
        print(f"Setting up {bulb_name} for color fade...")
        bulb = connect_device(device_configs[bulb_name])
        turn_on_bulb(bulb)
        bulbs[bulb_name] = bulb

    # Calculate program parameters
    duration_seconds = duration_minutes * 60
    steps_per_transition = 20  # More steps = smoother transition
    step_delay = transition_time / steps_per_transition

    # Track start time
    start_time = time.time()

    # Generate initial color
    current_color = generate_soft_color()

    # Apply initial color to all bulbs
    for name, bulb in bulbs.items():
        set_color(bulb, *current_color)
        print(f"Set initial color on {name}: RGB{current_color}")

    # Main program loop
    try:
        print(
            f"Starting color fade for {duration_minutes} minutes. Press Ctrl+C to exit."
        )
        print("Enjoy the relaxing color transitions...")

        transition_count = 0

        while running and (time.time() - start_time) < duration_seconds:
            transition_count += 1

            # Generate target color for this transition
            target_color = generate_soft_color()
            print(f"\nTransition {transition_count}: Fading to RGB{target_color}")

            # Gradually transition to the target color
            for step in range(1, steps_per_transition + 1):
                if not running:
                    break

                # Calculate interpolated color for this step
                interpolated_color = interpolate_color(
                    current_color, target_color, step, steps_per_transition
                )

                # Apply to all configured bulbs
                for name, bulb in bulbs.items():
                    set_color(bulb, *interpolated_color)

                # Wait for next step
                time.sleep(step_delay)

            # Update current color
            current_color = target_color

            # Display time remaining
            elapsed = time.time() - start_time
            remaining_minutes = max(0, (duration_seconds - elapsed) / 60)
            print(f"Time remaining: {remaining_minutes:.1f} minutes")

    except Exception as e:
        print(f"Error: {e}")

    print("Color fade program ended.")


if __name__ == "__main__":
    main()
