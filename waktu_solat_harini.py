import argparse
import json
import math
import textwrap
from ahc.sunmoon import set_location, fajr_time_utc, sunrise_sunset_utc, convert_utc_to_localtime
from skyfield import api, almanac
from datetime import timedelta, datetime

def load_locations(file_path):
    """Load predefined locations from a file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: location.txt file not found.")
        return {}

def format_time(dt):
    """Format time as 12-hour format (e.g., 7:35 PM), compatible with Windows & Unix."""
    return dt.strftime("%I:%M %p").lstrip("0")

def get_sun_altitude(ephem, location, t):
    """Calculate the sun's altitude at a given time."""
    observer = (ephem["Earth"] + location).at(t)
    sun = observer.observe(ephem["Sun"]).apparent()
    altitude, _, _ = sun.altaz()
    return altitude.degrees

def get_prayer_times(year, month, day, latitude, longitude, elevation, time_zone, loc_name, asr_method="shafi"):
    # Load ephemeris data
    ts = api.load.timescale()
    ephem = api.load_file('de421.bsp')
    
    # Set location
    location = set_location(latitude, longitude, elevation)
    
    # Malay translations for days and months
    malay_days = {"Monday": "Isnin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Khamis", "Friday": "Jumaat", "Saturday": "Sabtu", "Sunday": "Ahad"}
    malay_months = {"January": "Januari", "February": "Februari", "March": "Mac", "April": "April", "May": "Mei", "June": "Jun", "July": "Julai", "August": "Ogos", "September": "September", "October": "Oktober", "November": "November", "December": "Disember"}
    
    # Get day of the week and month name in Malay
    day_name = malay_days[datetime(year, month, day).strftime("%A")]
    month_name = malay_months[datetime(year, month, day).strftime("%B")]
    
    # 1. Get Fajr Time (UTC)
    fajr_utc = fajr_time_utc(location, year, month, day)
    
    # 2. Get Sunrise and Sunset (UTC)
    sunrise_utc, sunset_utc = sunrise_sunset_utc(location, year, month, day)
    
    # 3. Get Solar Noon (Dhuhr)
    t0 = ts.utc(year, month, day)
    t1 = ts.utc(year, month, day, 23, 59, 59)
    t, y = almanac.find_discrete(t0, t1, almanac.meridian_transits(ephem, ephem['Sun'], location))
    dhuhr_utc = t[0].utc_datetime()
    
    # 4. Calculate Asr (Using correct shadow length formula)
    shadow_ratio = 1 if asr_method == "shafi" else 2  # Shafi (1x shadow), Hanafi (2x shadow)
    
    # Get Sun altitude at Dhuhr
    t_dhuhr = ts.utc(dhuhr_utc.year, dhuhr_utc.month, dhuhr_utc.day, dhuhr_utc.hour, dhuhr_utc.minute)
    sun_alt_dhuhr = get_sun_altitude(ephem, location, t_dhuhr)
    
    # Compute required Asr altitude using tangent formula
    asr_altitude = math.degrees(math.atan(1 / (shadow_ratio + math.tan(math.radians(90 - sun_alt_dhuhr)))))
    
    # Find Asr time by iterating every 1 minute after Dhuhr
    t_asr = ts.utc(dhuhr_utc.year, dhuhr_utc.month, dhuhr_utc.day, dhuhr_utc.hour + 1)
    while get_sun_altitude(ephem, location, t_asr) > asr_altitude:
        t_asr = ts.utc(t_asr.utc_datetime() + timedelta(minutes=1))
    asr_utc = t_asr.utc_datetime()
    
    # 5. Maghrib (Same as Sunset)
    maghrib_utc = sunset_utc
    
    # 6. Calculate Isha (when Sun is -18° below horizon, step by 1 minute)
    t_isha = ts.utc(maghrib_utc.year, maghrib_utc.month, maghrib_utc.day, maghrib_utc.hour)
    while get_sun_altitude(ephem, location, t_isha) > -18:
        t_isha = ts.utc(t_isha.utc_datetime() + timedelta(minutes=1))
    isha_utc = t_isha.utc_datetime()
    
    # Convert to local time
    fajr_local = convert_utc_to_localtime(time_zone, fajr_utc)
    sunrise_local = convert_utc_to_localtime(time_zone, sunrise_utc)
    dhuhr_local = convert_utc_to_localtime(time_zone, dhuhr_utc)
    asr_local = convert_utc_to_localtime(time_zone, asr_utc)
    maghrib_local = convert_utc_to_localtime(time_zone, maghrib_utc)
    isha_local = convert_utc_to_localtime(time_zone, isha_utc)
    
    # Print formatted prayer times
    wrapped_loc_name = textwrap.wrap(loc_name, width=25)
    wrapped_loc_name = "\n".join(f"{line.center(36)}" for line in wrapped_loc_name)
    
    print("\n           Waktu Solat")
    print(f"   pada hari {day_name}, {day} {month_name} {year}")
    print("           bagi kawasan")
    print(f"{wrapped_loc_name}")
    print("====================================")
    print(f"        Subuh    : {format_time(fajr_local)}")
    print(f"        Syuruk   : {format_time(sunrise_local)}")
    print(f"        Zohor    : {format_time(dhuhr_local)}")
    print(f"        Asar     : {format_time(asr_local)}")
    print(f"        Maghrib  : {format_time(maghrib_local)}")
    print(f"        Isha     : {format_time(isha_local)}")

# Argument Parser
parser = argparse.ArgumentParser(description="Get Islamic prayer times for a given location and date.")
parser.add_argument("--date", type=str, default=datetime.today().strftime("%Y-%m-%d"), help="Date in YYYY-MM-DD format")
parser.add_argument("--location", type=str, default="home", help="Predefined location name (e.g., Perak, Kedah, Johor)")
parser.add_argument("--latitude", type=float, help="Latitude of the location")
parser.add_argument("--longitude", type=float, help="Longitude of the location")
parser.add_argument("--elevation", type=float, help="Elevation in meters")
parser.add_argument("--timezone", type=str, default="Asia/Kuala_Lumpur", help="Time zone (e.g., Asia/Kuala_Lumpur)")

args = parser.parse_args()

locations = load_locations("location.txt")

if args.location and args.location in locations:
    loc_data = locations[args.location]
    latitude, longitude, elevation, time_zone, loc_name = loc_data["latitude"], loc_data["longitude"], loc_data.get("elevation", 10), loc_data["timezone"], loc_data.get("remarks", args.location)
elif args.latitude and args.longitude and args.timezone:
    latitude, longitude, elevation, time_zone = args.latitude, args.longitude, args.elevation or 10, args.timezone
    loc_name = f"Latitude: {latitude}, Longitude: {longitude}, Elevation: {elevation}m"
else:
    print("Error: Provide either --location or --latitude, --longitude, --timezone.")
    exit(1)

year, month, day = map(int, args.date.split("-"))
get_prayer_times(year, month, day, latitude, longitude, elevation, time_zone, loc_name)
