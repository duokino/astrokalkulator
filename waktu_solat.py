import json
import math
import argparse
from datetime import datetime, timedelta
from ahc.sunmoon import set_location, fajr_time_utc, sunrise_sunset_utc, convert_utc_to_localtime
from skyfield import api, almanac

def load_locations(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: location.txt file not found.")
        return {}

def get_sun_altitude(ephem, location, t):
    observer = (ephem["Earth"] + location).at(t)
    sun = observer.observe(ephem["Sun"]).apparent()
    altitude, _, _ = sun.altaz()
    return altitude.degrees

def get_prayer_times(year, month, day, latitude, longitude, elevation, time_zone, asr_method="shafi"):
    ts = api.load.timescale()
    ephem = api.load_file('de421.bsp')
    location = set_location(latitude, longitude, elevation)

    fajr_utc = fajr_time_utc(location, year, month, day)
    sunrise_utc, sunset_utc = sunrise_sunset_utc(location, year, month, day)

    t0 = ts.utc(year, month, day)
    t1 = ts.utc(year, month, day, 23, 59, 59)
    t, _ = almanac.find_discrete(t0, t1, almanac.meridian_transits(ephem, ephem['Sun'], location))
    dhuhr_utc = t[0].utc_datetime()
    
    shadow_ratio = 1 if asr_method == "shafi" else 2
    
    t_dhuhr = ts.utc(dhuhr_utc.year, dhuhr_utc.month, dhuhr_utc.day, dhuhr_utc.hour, dhuhr_utc.minute)
    sun_alt_dhuhr = get_sun_altitude(ephem, location, t_dhuhr)
    
    asr_altitude = math.degrees(math.atan(1 / (shadow_ratio + math.tan(math.radians(90 - sun_alt_dhuhr)))))
    
    t_asr = ts.utc(dhuhr_utc.year, dhuhr_utc.month, dhuhr_utc.day, dhuhr_utc.hour + 1)
    while get_sun_altitude(ephem, location, t_asr) > asr_altitude:
        t_asr = ts.utc(t_asr.utc_datetime() + timedelta(minutes=1))
    asr_utc = t_asr.utc_datetime()
    
    # Adjust Maghrib time to when the whole sun is below the horizon (-1.066°) because Sun's apparent radius (~0.2665°) and refraction effect (~0.566° at horizon)
    t_maghrib = ts.utc(sunset_utc.year, sunset_utc.month, sunset_utc.day, sunset_utc.hour, sunset_utc.minute)
    while get_sun_altitude(ephem, location, t_maghrib) > -1.066:
        t_maghrib = ts.utc(t_maghrib.utc_datetime() + timedelta(minutes=1))
    maghrib_utc = t_maghrib.utc_datetime()
    
    t_isha = ts.utc(maghrib_utc.year, maghrib_utc.month, maghrib_utc.day, maghrib_utc.hour)
    while get_sun_altitude(ephem, location, t_isha) > -18:
        t_isha = ts.utc(t_isha.utc_datetime() + timedelta(minutes=1))
    isyak_utc = t_isha.utc_datetime()
    
    return {
        "Subuh": convert_utc_to_localtime(time_zone, fajr_utc).strftime("%I:%M %p"),
        "Syuruk": convert_utc_to_localtime(time_zone, sunrise_utc).strftime("%I:%M %p"),
        "Zohor": convert_utc_to_localtime(time_zone, dhuhr_utc).strftime("%I:%M %p"),
        "Asar": convert_utc_to_localtime(time_zone, asr_utc).strftime("%I:%M %p"),
        "Maghrib": convert_utc_to_localtime(time_zone, maghrib_utc).strftime("%I:%M %p"),
        "Isyak": convert_utc_to_localtime(time_zone, isyak_utc).strftime("%I:%M %p")
    }

malay_months_abbr = {
    "January": "Jan", "February": "Feb", "March": "Mac", "April": "Apr", "May": "Mei", "June": "Jun",
    "July": "Jul", "August": "Ogos", "September": "Sep", "October": "Okt", "November": "Nov", "December": "Dis"
}

def generate_monthly_prayer_times(year, month, latitude, longitude, elevation, time_zone, loc_name):
    days_in_month = (datetime(year, month % 12 + 1, 1) - timedelta(days=1)).day
    month_name = malay_months_abbr[datetime(year, month, 1).strftime('%B')]
    print(f"\n{'Waktu Solat bagi bulan ' + month_name + ' ' + str(year):^82}")
    print(f"{'bagi kawasan ' + loc_name:^82}")
    print("=" * 82)
    print("  Tarikh     Subuh       Syuruk      Zohor        Asar       Maghrib     Isyak")
    print("-" * 82)
    
    for day in range(1, days_in_month + 1):
        prayer_times = get_prayer_times(year, month, day, latitude, longitude, elevation, time_zone)
        print(f"  {day:2d} {month_name}  {prayer_times['Subuh']:>10}  {prayer_times['Syuruk']:>10}  {prayer_times['Zohor']:>10}  {prayer_times['Asar']:>10}  {prayer_times['Maghrib']:>10}  {prayer_times['Isyak']:>10}")
    print("=" * 82)

# Argument Parser
parser = argparse.ArgumentParser(description="Generate monthly Islamic prayer times.")
parser.add_argument("year", type=int, nargs="?", default=datetime.today().year, help="Year (default: current year)")
parser.add_argument("month", type=int, nargs="?", default=datetime.today().month, help="Month (default: current month)")
parser.add_argument("--location", default="home", type=str, help="Predefined location name (e.g., Perak, Kedah, Johor)")
parser.add_argument("--latitude", type=float, help="Latitude of the location")
parser.add_argument("--longitude", type=float, help="Longitude of the location")
parser.add_argument("--elevation", type=float, help="Elevation in meters")
parser.add_argument("--timezone", default="Asia/Kuala_Lumpur", type=str, help="Time zone (e.g., Asia/Kuala_Lumpur)")

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

generate_monthly_prayer_times(args.year, args.month, latitude, longitude, elevation, time_zone, loc_name)
