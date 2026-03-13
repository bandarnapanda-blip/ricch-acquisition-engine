from geopy.geocoders import Nominatim
import json
import time
from config import CITIES

geolocator = Nominatim(user_agent="ri2ch_digital_engine")

coords_map = {}

print("Fetching coordinates for cities...")
for city in CITIES:
    try:
        print(f"  Looking up: {city}")
        location = geolocator.geocode(city)
        if location:
            coords_map[city] = {
                "lat": location.latitude,
                "lon": location.longitude
            }
        else:
            print(f"  Warning: Could not find {city}")
        # Rate limit compliant
        time.sleep(1.1)
    except Exception as e:
        print(f"  Error fetching {city}: {e}")

with open("city_coords.json", "w") as f:
    json.dump(coords_map, f, indent=4)

print("\nSaved coordinates to city_coords.json")
