"""
Action handlers for Tuya smart bulb commands.

This module provides functions to route commands from the command-line
to the appropriate bulb command functions.
"""

from .bulb_commands import (
    turn_on_bulb,
    turn_off_bulb,
    set_brightness,
    set_temperature,
    set_color,
    get_status,
)


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
