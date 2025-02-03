# Meeting Point Mapper

## Overview

This project generates a map that identifies a common meeting area based on provided coordinates. It visualizes houses, their respective areas, and nearby restaurants using **Folium** and **Overpass API**.

## Features

- Reads house coordinates from `coords.txt`
- Reads color codes from `colors.txt`
- Converts coordinates to UTM format for accurate calculations
- Finds a common meeting area using intersection logic
- Fetches nearby restaurants using Overpass API
- Generates an interactive HTML map

## Requirements

Ensure you have Python installed, then install the required dependencies:

```sh
pip install -r requirements.txt
```

## File Structure

- `main.py` - Main script to generate the meeting map
- `requirements.txt` - List of required Python libraries
- `coords.txt` - Input file containing latitude and longitude of houses
- `colors.txt` - Input file containing color codes for markers
- `meeting_map.html` - Generated interactive map

## Usage

1. Place house coordinates in `coords.txt`, one per line in `@lat,lon` format (e.g., `@24.8020962,67.0298298`). These coordinates can be obtained from Google Maps URL (e.g., `https://www.google.com/maps/@24.8652276,67.0315489,18.25z`).
2. Specify marker colors in `colors.txt`, one color per line (avoid hexcodes as it will have issues in marking houses e.g., `#FF5733`).
3. Run the script:

```sh
python main.py
```

4. Open `meeting_map.html` to view the generated map.

## Example Inputs

### `coords.txt`

```
@37.7749,-122.4194
@37.7849,-122.4094
@37.7649,-122.4294
```

### `colors.txt`

```
#FF5733
#33FF57
#3357FF
```

## Output

- Markers for houses with corresponding colors.
- Circular areas representing house influence zones.
- A polygon marking the common meeting area.
- Nearby restaurants marked in green.

## Troubleshooting

- If `colors.txt` is missing, a default color (`red`) will be used.
- If no common meeting area is found, ensure coordinates are valid and within range.
- If API requests fail, check internet connection or retry after some time.
