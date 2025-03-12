#!/usr/bin/env python3
"""
Tuya Smart Bulb Server

This server provides a web interface to manage Tuya smart bulbs, allowing users to:
- View all bulbs and their status
- Change bulb colors and brightness
- Run lighting programs for specified durations
"""

import os
import time
import json
import threading
import importlib
import signal
import sys
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

# Import our custom modules
from utils.device_manager import setup_devices, connect_device
from commands.bulb_commands import (
    turn_on_bulb,
    turn_off_bulb,
    set_brightness,
    set_temperature,
    set_color,
    get_status,
)

# Create Flask app and SocketIO instance
app = Flask(__name__)
app.config["SECRET_KEY"] = "smarthome-secret-key!"
socketio = SocketIO(app)

# Global variables
bulbs = {}  # Store our bulb devices
program_threads = {}  # Track running program threads
stop_events = {}  # Events to signal programs to stop


# Setup Tuya devices
def initialize_devices():
    """Initialize and connect to all bulb devices"""
    global bulbs
    device_configs = setup_devices()

    for name, config in device_configs.items():
        try:
            # Connect to the device
            device = connect_device(config)
            # Store in our global bulbs dictionary
            bulbs[name] = {
                "device": device,
                "config": config,
                "name": name,
                "status": {"online": True},
            }
            # Update status
            try:
                status_data = device.status()
                if "dps" in status_data:
                    bulbs[name]["status"] = {
                        "online": True,
                        "power": status_data["dps"].get("20", False),
                        "mode": status_data["dps"].get("21", "unknown"),
                        "brightness": status_data["dps"].get("22", 0),
                        "temperature": status_data["dps"].get("23", 0),
                        "color_data": status_data["dps"].get("24", None),
                    }
            except Exception as e:
                print(f"Error getting status for {name}: {e}")
                bulbs[name]["status"] = {"online": False, "error": str(e)}
        except Exception as e:
            print(f"Error connecting to {name}: {e}")
            bulbs[name] = {
                "config": config,
                "name": name,
                "status": {"online": False, "error": str(e)},
            }

    return bulbs


# Function to run a program
def run_program(program_name, bulb_name, duration, socket_io):
    """Run a lighting program for a specific duration"""
    # Import the program module
    try:
        print(
            f"Attempting to run program: {program_name} on bulb: {bulb_name} for {duration} seconds"
        )

        # Get the stop event
        stop_event = stop_events.get(f"{bulb_name}_{program_name}", threading.Event())
        stop_events[f"{bulb_name}_{program_name}"] = stop_event

        # Add programs directory to path if needed
        programs_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "programs"
        )
        if programs_dir not in sys.path:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            print(f"Added {os.path.dirname(os.path.abspath(__file__))} to sys.path")

        # Import the module
        module_path = f"programs.{program_name}"
        print(f"Importing module: {module_path}")
        print(f"Python path: {sys.path}")
        try:
            program_module = importlib.import_module(module_path)
            print(f"Successfully imported module: {module_path}")
            print(f"Module methods: {dir(program_module)}")
        except Exception as e:
            print(f"Error importing module {module_path}: {e}")
            import traceback

            traceback.print_exc()
            raise

        # Run the program
        device = bulbs[bulb_name]["device"] if bulb_name in bulbs else None

        if not device and bulb_name != "all_bulbs":
            raise ValueError(f"No device found for bulb: {bulb_name}")

        if device or bulb_name == "all_bulbs":
            # Get the bulb devices list if using all_bulbs
            devices_list = None
            if bulb_name == "all_bulbs":
                devices_list = [
                    info["device"] for name, info in bulbs.items() if "device" in info
                ]
                print(f"Running on all_bulbs: {len(devices_list)} devices")
            else:
                print(f"Running on single bulb: {bulb_name}")

            # Check if run_program function exists in the module
            if hasattr(program_module, "run_program"):
                print(f"Found run_program function in {program_name}")
                socket_io.emit(
                    "program_status",
                    {
                        "bulb": bulb_name,
                        "program": program_name,
                        "status": "running",
                        "duration": duration,
                    },
                )

                # Run the program with the stop event
                try:
                    if bulb_name == "all_bulbs" and devices_list:
                        print(
                            f"Calling run_program for all_bulbs with {len(devices_list)} devices"
                        )
                        program_module.run_program(
                            devices_list, duration=duration, stop_event=stop_event
                        )
                    else:
                        print(f"Calling run_program for {bulb_name}")
                        program_module.run_program(
                            device, duration=duration, stop_event=stop_event
                        )
                    print(f"Program {program_name} completed successfully")
                except Exception as e:
                    print(f"Error in program execution: {e}")
                    import traceback

                    traceback.print_exc()
                    socket_io.emit(
                        "program_status",
                        {
                            "bulb": bulb_name,
                            "program": program_name,
                            "status": "error",
                            "error": str(e),
                        },
                    )
                    return

                socket_io.emit(
                    "program_status",
                    {"bulb": bulb_name, "program": program_name, "status": "completed"},
                )
            else:
                # Fall back to main function
                print(
                    f"No run_program function found in {program_name}, falling back to main()"
                )
                # Create sys.argv-like arguments for the program
                old_argv = sys.argv.copy()
                if duration:
                    sys.argv = [program_name, bulb_name, str(duration)]
                else:
                    sys.argv = [program_name, bulb_name]

                # Redirect program output
                socket_io.emit(
                    "program_status",
                    {
                        "bulb": bulb_name,
                        "program": program_name,
                        "status": "running",
                        "duration": duration,
                    },
                )

                # Run the program
                if hasattr(program_module, "main"):
                    try:
                        program_module.main()
                        print(f"Program {program_name} main() completed successfully")
                    except Exception as e:
                        print(f"Error in program main(): {e}")
                        import traceback

                        traceback.print_exc()
                        socket_io.emit(
                            "program_status",
                            {
                                "bulb": bulb_name,
                                "program": program_name,
                                "status": "error",
                                "error": str(e),
                            },
                        )
                        return

                # Restore sys.argv
                sys.argv = old_argv

                socket_io.emit(
                    "program_status",
                    {"bulb": bulb_name, "program": program_name, "status": "completed"},
                )

    except Exception as e:
        print(f"Error running program {program_name} on {bulb_name}: {e}")
        import traceback

        traceback.print_exc()
        socketio.emit(
            "program_status",
            {
                "bulb": bulb_name,
                "program": program_name,
                "status": "error",
                "error": str(e),
            },
        )

    # Clean up
    if f"{bulb_name}_{program_name}" in program_threads:
        del program_threads[f"{bulb_name}_{program_name}"]
    if f"{bulb_name}_{program_name}" in stop_events:
        del stop_events[f"{bulb_name}_{program_name}"]


# Routes
@app.route("/")
def index():
    """Main page route"""
    return render_template("index.html")


@app.route("/api/bulbs", methods=["GET"])
def get_bulbs():
    """Get all bulbs and their status"""
    # Refresh status for each bulb
    for name, bulb_info in bulbs.items():
        if "device" in bulb_info:
            try:
                status_data = bulb_info["device"].status()
                if "dps" in status_data:
                    bulbs[name]["status"] = {
                        "online": True,
                        "power": status_data["dps"].get("20", False),
                        "mode": status_data["dps"].get("21", "unknown"),
                        "brightness": status_data["dps"].get("22", 0),
                        "temperature": status_data["dps"].get("23", 0),
                        "color_data": status_data["dps"].get("24", None),
                    }
            except Exception as e:
                print(f"Error getting status for {name}: {e}")
                bulbs[name]["status"] = {"online": False, "error": str(e)}

    # Format the response
    bulb_data = {}
    for name, bulb_info in bulbs.items():
        bulb_data[name] = {"name": name, "status": bulb_info["status"]}

    return jsonify(bulb_data)


@app.route("/api/bulbs/<bulb_name>/toggle", methods=["POST"])
def toggle_bulb(bulb_name):
    """Toggle a bulb on or off"""
    if bulb_name not in bulbs or "device" not in bulbs[bulb_name]:
        return jsonify({"error": f"Bulb {bulb_name} not found or offline"}), 404

    device = bulbs[bulb_name]["device"]
    current_status = device.status()

    if "dps" in current_status and "20" in current_status["dps"]:
        is_on = current_status["dps"]["20"]
        if is_on:
            turn_off_bulb(device)
            bulbs[bulb_name]["status"]["power"] = False
        else:
            turn_on_bulb(device)
            bulbs[bulb_name]["status"]["power"] = True

        # Emit status update via Socket.IO
        socketio.emit(
            "bulb_update", {"bulb": bulb_name, "status": bulbs[bulb_name]["status"]}
        )

        return jsonify({"status": "success", "power": not is_on})

    return jsonify({"error": "Failed to get current status"}), 500


@app.route("/api/bulbs/<bulb_name>/brightness", methods=["POST"])
def set_bulb_brightness(bulb_name):
    """Set bulb brightness"""
    if bulb_name not in bulbs or "device" not in bulbs[bulb_name]:
        return jsonify({"error": f"Bulb {bulb_name} not found or offline"}), 404

    data = request.json
    if "brightness" not in data:
        return jsonify({"error": "Brightness value not provided"}), 400

    brightness = int(data["brightness"])
    device = bulbs[bulb_name]["device"]

    result = set_brightness(device, brightness)
    if result:
        bulbs[bulb_name]["status"]["brightness"] = brightness
        # Emit status update via Socket.IO
        socketio.emit(
            "bulb_update", {"bulb": bulb_name, "status": bulbs[bulb_name]["status"]}
        )
        return jsonify({"status": "success", "brightness": brightness})

    return jsonify({"error": "Failed to set brightness"}), 500


@app.route("/api/bulbs/<bulb_name>/temperature", methods=["POST"])
def set_bulb_temperature(bulb_name):
    """Set bulb color temperature"""
    if bulb_name not in bulbs or "device" not in bulbs[bulb_name]:
        return jsonify({"error": f"Bulb {bulb_name} not found or offline"}), 404

    data = request.json
    if "temperature" not in data:
        return jsonify({"error": "Temperature value not provided"}), 400

    temperature = int(data["temperature"])
    device = bulbs[bulb_name]["device"]

    result = set_temperature(device, temperature)
    if result:
        bulbs[bulb_name]["status"]["temperature"] = temperature
        # Emit status update via Socket.IO
        socketio.emit(
            "bulb_update", {"bulb": bulb_name, "status": bulbs[bulb_name]["status"]}
        )
        return jsonify({"status": "success", "temperature": temperature})

    return jsonify({"error": "Failed to set temperature"}), 500


@app.route("/api/bulbs/<bulb_name>/color", methods=["POST"])
def set_bulb_color(bulb_name):
    """Set bulb color using RGB values"""
    if bulb_name not in bulbs or "device" not in bulbs[bulb_name]:
        return jsonify({"error": f"Bulb {bulb_name} not found or offline"}), 404

    data = request.json
    if not all(key in data for key in ["r", "g", "b"]):
        return jsonify({"error": "RGB color values not provided"}), 400

    r = int(data["r"])
    g = int(data["g"])
    b = int(data["b"])
    device = bulbs[bulb_name]["device"]

    result = set_color(device, r, g, b)
    if result:
        # Emit status update via Socket.IO
        socketio.emit(
            "bulb_update",
            {"bulb": bulb_name, "status": {"color": {"r": r, "g": g, "b": b}}},
        )
        return jsonify({"status": "success", "color": {"r": r, "g": g, "b": b}})

    return jsonify({"error": "Failed to set color"}), 500


@app.route("/api/programs", methods=["GET"])
def get_programs():
    """Get available lighting programs"""
    programs = []
    program_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "programs")

    for filename in os.listdir(program_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            program_name = filename.replace(".py", "")
            programs.append(program_name)

    return jsonify({"programs": programs})


@app.route("/api/programs/run", methods=["POST"])
def run_program_api():
    """Run a lighting program"""
    data = request.json
    print(f"Program run request: {data}")

    if not all(key in data for key in ["program", "bulb"]):
        error_msg = "Program and bulb name must be provided"
        print(f"API error: {error_msg}")
        return jsonify({"error": error_msg}), 400

    program = data["program"]
    bulb_name = data["bulb"]
    duration = data.get("duration", 60)  # Default 60 seconds if not specified

    print(
        f"Processing program run request: program={program}, bulb={bulb_name}, duration={duration}"
    )

    # Check if bulb exists
    if bulb_name != "all_bulbs" and (
        bulb_name not in bulbs or "device" not in bulbs[bulb_name]
    ):
        error_msg = f"Bulb {bulb_name} not found or offline"
        print(f"API error: {error_msg}")
        return jsonify({"error": error_msg}), 404

    # Check if program exists
    program_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "programs", f"{program}.py"
    )
    if not os.path.exists(program_path):
        error_msg = f"Program {program} not found at {program_path}"
        print(f"API error: {error_msg}")
        return jsonify({"error": error_msg}), 404

    print(f"Program file found: {program_path}")

    # Stop any running program for this bulb
    thread_key = f"{bulb_name}_{program}"
    if thread_key in program_threads and program_threads[thread_key].is_alive():
        print(f"Stopping existing program: {thread_key}")
        if thread_key in stop_events:
            stop_events[thread_key].set()  # Signal the thread to stop
        program_threads[thread_key].join(timeout=2)  # Wait for it to stop

    # Create a stop event
    stop_event = threading.Event()
    stop_events[thread_key] = stop_event

    print(f"Created stop event: {thread_key}")

    # Start the program in a new thread
    thread = threading.Thread(
        target=run_program, args=(program, bulb_name, duration, socketio), daemon=True
    )
    program_threads[thread_key] = thread

    print(f"Starting thread for program: {thread_key}")
    thread.start()

    return jsonify(
        {
            "status": "success",
            "message": f"Program {program} started on {bulb_name} for {duration} seconds",
        }
    )


@app.route("/api/programs/stop", methods=["POST"])
def stop_program():
    """Stop a running program"""
    data = request.json
    if not all(key in data for key in ["program", "bulb"]):
        return jsonify({"error": "Program and bulb name must be provided"}), 400

    program = data["program"]
    bulb_name = data["bulb"]

    thread_key = f"{bulb_name}_{program}"
    if thread_key in program_threads and program_threads[thread_key].is_alive():
        if thread_key in stop_events:
            stop_events[thread_key].set()  # Signal the thread to stop

        # Wait for the thread to stop
        program_threads[thread_key].join(timeout=2)

        # Clean up
        if thread_key in program_threads:
            del program_threads[thread_key]
        if thread_key in stop_events:
            del stop_events[thread_key]

        socketio.emit(
            "program_status",
            {"bulb": bulb_name, "program": program, "status": "stopped"},
        )

        return jsonify({"status": "success", "message": f"Program {program} stopped"})

    return (
        jsonify(
            {
                "status": "error",
                "message": f"No running program {program} found for {bulb_name}",
            }
        ),
        404,
    )


# Main entry point
if __name__ == "__main__":
    # Initialize devices
    print("Initializing smart bulb devices...")
    initialize_devices()
    print(f"Found {len(bulbs)} bulbs")

    # Set up signal handler for clean exit
    def signal_handler(sig, frame):
        print("Shutting down...")
        # Stop all running programs
        for key, event in stop_events.items():
            event.set()
        for key, thread in program_threads.items():
            thread.join(timeout=1)
        # Exit
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Start the server
    print("Starting server on http://0.0.0.0:3456")
    socketio.run(app, host="0.0.0.0", port=3456, debug=True, use_reloader=False)
