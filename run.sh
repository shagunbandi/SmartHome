#!/bin/bash

# Load environment variables if .env file exists
if [ -f .env ]; then
  echo "Loading environment variables from .env file..."
  source .env
else
  # Check if this is the first run
  if [ ! -f .env.example ]; then
    # Create .env.example file
    echo "# Tuya API Credentials" > .env.example
    echo "TUYA_API_KEY=your_api_key_here" >> .env.example
    echo "TUYA_API_SECRET=your_api_secret_here" >> .env.example
    echo "TUYA_REGION=eu" >> .env.example
    
    # Create .env file
    cp .env.example .env
    echo "Created .env file. Please edit it with your Tuya credentials."
    echo ""
  fi
  
  echo "No .env file found. Please create one with your Tuya credentials:"
  echo "TUYA_API_KEY=your_api_key_here"
  echo "TUYA_API_SECRET=your_api_secret_here"
  echo "TUYA_REGION=eu" 
  echo ""
  echo "You can copy the .env.example file to .env and edit it."
  echo ""
fi

# Check if required environment variables are set
if [ -z "$TUYA_API_KEY" ] || [ -z "$TUYA_API_SECRET" ]; then
  echo "Warning: Tuya API credentials not set in environment variables."
  echo "Some features may not work properly."
  echo ""
fi

# Check if devices.json file exists
if [ ! -f devices.json ]; then
  echo "devices.json file not found. Do you want to run the TinyTuya wizard to create it? (y/n)"
  read -r run_wizard
  if [ "$run_wizard" = "y" ] || [ "$run_wizard" = "Y" ]; then
    echo "Running TinyTuya wizard..."
    if [ -n "$TUYA_API_KEY" ] && [ -n "$TUYA_API_SECRET" ] && [ -n "$TUYA_REGION" ]; then
      python -m tinytuya wizard -key "$TUYA_API_KEY" -secret "$TUYA_API_SECRET" -region "$TUYA_REGION"
    else
      python -m tinytuya wizard
    fi
  else
    echo "Continuing without devices.json. The script may not work properly."
  fi
fi

# Check if arguments were provided
if [ $# -eq 0 ]; then
  echo "Usage: ./run.sh <bulb_name> <command> [value]"
  echo "Examples:"
  echo "  ./run.sh top on"
  echo "  ./run.sh middle brightness 500"
  echo "  ./run.sh bottom color 255 0 0"
  echo "  ./run.sh all_bulbs off"
  exit 1
fi

# Execute the Python script with all arguments
python tuya_control.py "$@" 