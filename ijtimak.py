import argparse
import json
from ahc.anakbulan import crescent_data

# Load predefined locations from location.txt
LOCATIONS_FILE = "database/location.txt"

def load_locations():
    try:
        with open(LOCATIONS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

LOCATIONS = load_locations()

def main():
    parser = argparse.ArgumentParser(description="Mengira data hilal berdasarkan tahun dan bulan Hijriah.")
    
    # Required arguments
    parser.add_argument("hijri_year", type=int, help="Tahun Hijriah")
    parser.add_argument("hijri_month", type=int, help="Bulan Hijriah")
    
    # Location selection argument
    parser.add_argument("--location", type=str, choices=LOCATIONS.keys(), default="home")

    # Day offset argument
    parser.add_argument("--offset", type=float, default=0, help="Day offset (default: 0)")    

    # Optional manual input arguments
    parser.add_argument("--latitude", type=float, help="Latitud lokasi")
    parser.add_argument("--longitude", type=float, help="Longitud lokasi")
    parser.add_argument("--elevation", type=float, help="Elevation dalam meter")
    parser.add_argument("--time_zone", type=str, default="Asia/Kuala_Lumpur", help="Time zone (default: Asia/Kuala_Lumpur)")
    parser.add_argument("--loc_name", type=str, help="Nama lokasi (default: Pantai Minyak Beku)")
    
    args = parser.parse_args()
    
    # Use predefined location if selected
    if args.location and args.location in LOCATIONS:
        loc_data = LOCATIONS[args.location]
        latitude = args.latitude if args.latitude else loc_data["latitude"]
        longitude = args.longitude if args.longitude else loc_data["longitude"]
        elevation = args.elevation if args.elevation else loc_data["elevation"]
        loc_name = loc_data.get("remarks", "No remarks available")
    else:
        # Use manually provided values or defaults
        latitude = args.latitude if args.latitude else 3.1528
        longitude = args.longitude if args.longitude else 101.7038
        elevation = args.elevation if args.elevation else 421
        loc_name = loc_data.get("remarks", "No remarks available")

    # Call the crescent_data function with user inputs
    crescent_data(
        hijri_year=args.hijri_year,
        hijri_month=args.hijri_month,
        latitude=latitude,
        longitude=longitude,
        elevation=elevation,
        time_zone_str=args.time_zone,
        loc_name=loc_name,
        delta_day=args.offset
    )

if __name__ == "__main__":
    main()
