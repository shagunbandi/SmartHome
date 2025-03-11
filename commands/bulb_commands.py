"""
Commands for controlling Tuya smart bulbs.

This module provides functions to control Tuya bulbs with commands
like turning them on/off, setting brightness, color, etc.
"""

import json


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
