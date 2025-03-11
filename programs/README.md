# Tuya Smart Bulb Programs

This directory contains various programs to control your Tuya smart bulbs with different lighting effects.

## Available Programs

### 1. Random Colors (`random_colors.py`)

Changes bulb colors randomly at set intervals.

```bash
# Usage
python programs/random_colors.py [bulb_name] [interval_seconds]

# Examples
python programs/random_colors.py top 2         # Change top bulb every 2 seconds
python programs/random_colors.py all_bulbs 5   # Change all bulbs every 5 seconds
```

### 2. Disco Mode (`disco_mode.py`)

Creates a disco-like effect with rapid color changes, focusing on vibrant colors.

```bash
# Usage
python programs/disco_mode.py [bulb_name] [duration_seconds]

# Examples
python programs/disco_mode.py top 30          # Disco mode on top bulb for 30 seconds
python programs/disco_mode.py all_bulbs 60    # Disco mode on all bulbs for 60 seconds
```

### 3. Color Fade (`color_fade.py`)

Creates smooth, gradual transitions between colors for a relaxing effect.

```bash
# Usage
python programs/color_fade.py [bulb_name] [duration_minutes]

# Examples
python programs/color_fade.py top 10          # Color fade on top bulb for 10 minutes
python programs/color_fade.py all_bulbs 30    # Color fade on all bulbs for 30 minutes
```

## Notes

- All programs can be stopped by pressing Ctrl+C
- If no bulb name is specified, the program will default to controlling all bulbs
- Each program has default values for intervals/durations if not specified 