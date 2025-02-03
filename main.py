import utm
import requests
import time
from shapely.geometry import Point
from shapely.ops import unary_union
import folium

DEFAULT_COLOR_PALETTE = "red"
DEFAULT_COMMON_AREA_COLOR = "yellow"

COLOR_PALETTE = []

def read_color_codes():
    global COLOR_PALETTE
    file_path = "colors.txt"
    
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                
                COLOR_PALETTE.append(line)
    
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found, using default color.")
        COLOR_PALETTE = [DEFAULT_COLOR_PALETTE]

def get_coordinates():
    with open("coords.txt", "r", encoding="utf-8") as file:
        return [line.strip() for line in file]

def parse_coordinate(coord_str):
    try:
        clean_str = coord_str.lstrip('@').split(',')
        return float(clean_str[0]), float(clean_str[1])
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid coordinate: {coord_str}") from e

def get_restaurants_with_retry(polygon_wkt, max_retries=3):
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["amenity"="restaurant"](poly:"{polygon_wkt}");
      way["amenity"="restaurant"](poly:"{polygon_wkt}");
      relation["amenity"="restaurant"](poly:"{polygon_wkt}");
    );
    out center;
    """
    
    for attempt in range(max_retries):
        try:
            response = requests.post(overpass_url, data=query, timeout=10)
            response.raise_for_status()
            return response.json()['elements']
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Retry {attempt + 1}/{max_retries}...")
                time.sleep(2 ** attempt)
            else:
                print(f"Restaurant fetch failed: {e}")
                return []
    return []

def main(radius):
    read_color_codes()
    input_coords = get_coordinates()
    houses = []
    for idx, coord in enumerate(input_coords):
        try:
            lat, lon = parse_coordinate(coord)
            houses.append((lat, lon, idx))
        except ValueError as e:
            print(e)
            return

    if not houses:
        print("No valid coordinates.")
        return

    utm_coords = []
    zones = set()
    for lat, lon, _ in houses:
        easting, northing, zone_num, zone_letter = utm.from_latlon(lat, lon)
        utm_coords.append((easting, northing))
        zones.add((zone_num, zone_letter))

    if len(zones) != 1:
        print("Multiple UTM zones.")
        return

    zone_num, zone_letter = zones.pop()
    buffers = [Point(easting, northing).buffer(radius) for easting, northing in utm_coords]

    intersection = buffers[0]
    for buf in buffers[1:]:
        intersection = intersection.intersection(buf)
        if intersection.is_empty:
            print("No common area.")
            return

    avg_lat = sum(lat for lat, _, _ in houses) / len(houses)
    avg_lon = sum(lon for _, lon, _ in houses) / len(houses)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

    for lat, lon, idx in houses:
        color = COLOR_PALETTE[idx % len(COLOR_PALETTE)]
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color=color, icon='home'),
            tooltip=f"House {idx+1}"
        ).add_to(m)

        folium.Circle(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.1
        ).add_to(m)

    common_area_poly = []
    if intersection.geom_type == 'MultiPolygon':
        polygons = list(intersection.geoms)
    else:
        polygons = [intersection]

    for poly in polygons:
        exterior = poly.exterior
        lat_lon_coords = [
            utm.to_latlon(x, y, zone_num, zone_letter)
            for x, y in exterior.coords
        ]
        common_area_poly.extend([(lat, lon) for lat, lon in lat_lon_coords])
        
        folium.Polygon(
            locations=lat_lon_coords,
            color=DEFAULT_COMMON_AREA_COLOR,
            fill=True,
            fill_color=DEFAULT_COMMON_AREA_COLOR,
            fill_opacity=0.4,
            popup="Common Meeting Area"
        ).add_to(m)

    if common_area_poly:
        poly_wkt = " ".join([f"{lat} {lon}" for lat, lon in common_area_poly])
        restaurants = get_restaurants_with_retry(poly_wkt)
        
        restaurant_count = 0
        for restaurant in restaurants:
            try:
                lat = restaurant.get('lat') or restaurant.get('center', {}).get('lat')
                lon = restaurant.get('lon') or restaurant.get('center', {}).get('lon')
                name = restaurant.get('tags', {}).get('name', 'Unnamed Restaurant')
                
                if lat and lon:
                    folium.Marker(
                        location=[lat, lon],
                        icon=folium.Icon(color='green', icon='utensils', prefix='fa'),
                        popup=name,
                        tooltip="Restaurant"
                    ).add_to(m)
                    restaurant_count += 1
            except Exception as e:
                print(f"Skipping invalid restaurant: {e}")
        
        print(f"Found {restaurant_count} restaurants in common area")

    m.save('meeting_map.html')
    print("Map saved successfully")

if __name__ == "__main__":
    radius_km = 8.5
    main(radius_km * 1000)