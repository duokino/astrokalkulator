import json
import argparse
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pytz
import time
from matplotlib.widgets import Button
from ahc.sunmoon import set_location, sun_position_time_local

def load_location_data(location_name):
    with open("database/location.txt", "r") as file:
        locations = json.load(file)
    
    if location_name not in locations:
        raise ValueError(f"Location '{location_name}' not found in location.txt")
    
    return locations[location_name]

def calculate_qibla_direction(lat, lon):
    kaabah_lat, kaabah_lon = 21.4225, 39.8262
    lat_rad, lon_rad = np.radians(lat), np.radians(lon)
    kaabah_lat_rad, kaabah_lon_rad = np.radians(kaabah_lat), np.radians(kaabah_lon)
    delta_lon = kaabah_lon_rad - lon_rad
    x = np.sin(delta_lon) * np.cos(kaabah_lat_rad)
    y = np.cos(lat_rad) * np.sin(kaabah_lat_rad) - np.sin(lat_rad) * np.cos(kaabah_lat_rad) * np.cos(delta_lon)
    qibla_azimuth = np.degrees(np.arctan2(x, y))
    return (qibla_azimuth + 360) % 360

def toggle_realtime(event):
    global realtime, btn_realtime, use_original_time
    realtime = not realtime
    use_original_time = not realtime  # Restore original date_time when turning off realtime
    btn_realtime.label.set_text("Realtime: ON" if realtime else "Realtime: OFF")
    btn_realtime.color = 'lightgreen' if realtime else 'lightgrey'
    plt.draw()

def exit_program(event):
    plt.close()
    exit()

def plot_shadow_direction(location, location_data, qibla_azimuth, original_date_time):
    global realtime, btn_realtime, use_original_time
    realtime = False
    use_original_time = True  # Start with provided date_time
    timezone = pytz.timezone(location_data["timezone"])
    date_time = original_date_time
    
    fig, ax = plt.subplots(figsize=(8, 8))
    plt.subplots_adjust(bottom=0.3)
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    
    btn_realtime_ax = plt.axes([0.35, 0.23, 0.2, 0.05])
    btn_realtime = Button(btn_realtime_ax, "Realtime: OFF", color='lightgrey')
    btn_realtime.on_clicked(toggle_realtime)
    
    btn_exit_ax = plt.axes([0.6, 0.23, 0.1, 0.05])
    btn_exit = Button(btn_exit_ax, "TUTUP", color='red')
    btn_exit.on_clicked(exit_program)
    
    while True:
        if realtime:
            date_time = datetime.now(timezone)
        elif use_original_time:
            date_time = original_date_time  # Restore original date_time
            use_original_time = False  # Ensure it doesn't keep resetting
        
        sun_alt, sun_az, _ = sun_position_time_local(location, location_data["timezone"], local_datetime=date_time)
        
        ax.clear()
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect('equal')
        ax.set_title(f"Arah Bayang-Bayang Matahari\n{location_data['remarks']}\nTarikh: {date_time.strftime('%Y-%m-%d')}  Masa: {date_time.strftime('%I:%M:%S %p')}\nArah Kiblat: {qibla_azimuth:.2f}°")
        fig.text(0.52, 0.16, "Ini merupakan janaan dari python menggunakan pengiraan ahc\nbagi menentukan arah kiblat berpandukan bayang-bayang matahari\n@duokino", ha='center', fontsize=10, style='italic', color='gray')
        
        circle = plt.Circle((0, 0), 1, color='black', fill=False, linewidth=1.5)
        ax.add_patch(circle)
        
        for angle in range(0, 360, 10):
            angle_rad = np.radians(angle)
            x_outer, y_outer = np.cos(angle_rad), np.sin(angle_rad)
            x_inner, y_inner = 0.9 * x_outer, 0.9 * y_outer
            ax.plot([x_inner, x_outer], [y_inner, y_outer], color='black', linewidth=0.8)
        
        sun_angle_rad = np.radians(sun_az)
        qibla_angle_rad = np.radians(qibla_azimuth)
        x_sun, y_sun = -np.sin(sun_angle_rad), -np.cos(sun_angle_rad)
        x_qibla, y_qibla = np.sin(qibla_angle_rad), np.cos(qibla_angle_rad)
        
        ax.arrow(0, 0, x_sun, y_sun, head_width=0.05, head_length=0.1, fc='black', ec='black')
        ax.arrow(0, 0, 0, 1, head_width=0.05, head_length=0.1, fc='red', ec='red')
        ax.arrow(0, 0, x_qibla, y_qibla, head_width=0.05, head_length=0.1, fc='green', ec='green')
        
        ax.text(0, 1.1, "U", ha='center', fontsize=12, fontweight='bold', color='red')
        ax.text(1.1, 0, "T", va='center', fontsize=12, fontweight='bold')
        ax.text(-1.15, 0, "B", va='center', fontsize=12, fontweight='bold')
        ax.text(0, -1.15, "S", ha='center', fontsize=12, fontweight='bold')
        ax.text(x_qibla * 1.2, y_qibla * 1.2, "Kiblat", ha='center', fontsize=12, fontweight='bold', color='green')
        
        plt.draw()
        plt.pause(5)

def main():
    parser = argparse.ArgumentParser(description="Calculate sun shadow direction.")
    parser.add_argument("--location", default="bp", help="Location name from location.txt")
    parser.add_argument("--date", help="Date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--time", help="Time in HH:MM:SS format (default: now)")
    args = parser.parse_args()
    
    location_data = load_location_data(args.location)
    location = set_location(location_data["latitude"], location_data["longitude"], location_data["elevation"])
    timezone = pytz.timezone(location_data["timezone"])
    
    now = datetime.now(timezone)
    date_str = args.date if args.date else now.strftime("%Y-%m-%d")
    time_str = args.time if args.time else now.strftime("%H:%M:%S")
    
    date_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    date_time = timezone.localize(date_time)
    
    qibla_azimuth = calculate_qibla_direction(location_data["latitude"], location_data["longitude"])
    
    plot_shadow_direction(location, location_data, qibla_azimuth, date_time)

if __name__ == "__main__":
    main()
