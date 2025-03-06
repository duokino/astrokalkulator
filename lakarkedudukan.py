import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import os
import json
from ahc.sunmoon import set_location, sun_position_time_local, moon_position_time_local, sunrise_sunset_local

def load_location(location_name):
    location_file = os.path.join("database", "location.txt")
    with open(location_file, "r") as file:
        locations = json.load(file)
        if location_name in locations:
            loc = locations[location_name]
            return loc["latitude"], loc["longitude"], loc["elevation"], loc["timezone"], loc["remarks"]
    raise ValueError(f"Location '{location_name}' not found in {location_file}")

def plot_sun_moon(date, latitude, longitude, elevation, timezone, location_label, kriteria, time):
    location = set_location(latitude, longitude, elevation)
    year, month, day = map(int, date.split('-'))
    
    if time:
        hour, minute = int(time[:2]), int(time[2:])
    else:
        _, sunset_time = sunrise_sunset_local(location, timezone, year=year, month=month, day=day)
        
        # Find the time when the whole sun is below the horizon (altitude < -0.53°)
        temp_hour, temp_minute, temp_second = sunset_time.hour, sunset_time.minute, sunset_time.second
        while True:
            sun_alt, _, _ = sun_position_time_local(location, timezone, 
                                                    year=year, month=month, day=day, 
                                                    hour=temp_hour, minute=temp_minute, second=temp_second)
            if sun_alt < -0.53:  # Sun fully below the horizon (full diameter)
                break
            
            # Move forward in time by 10 seconds for better accuracy
            temp_second += 10
            if temp_second >= 60:
                temp_second = 0
                temp_minute += 1
            if temp_minute == 60:
                temp_minute = 0
                temp_hour += 1
        
        hour, minute = temp_hour, temp_minute
    
    # Get sun and moon altitude angles at the specified time
    sun_alt, _, _ = sun_position_time_local(location, timezone, year=year, month=month, day=day, hour=hour, minute=minute, second=0)
    moon_alt, _, _ = moon_position_time_local(location, timezone, year=year, month=month, day=day, hour=hour, minute=minute, second=0)
    
    # Angular sizes (approximate values in degrees)
    sun_angular_size = 0.53
    moon_angular_size = 0.50
    
    # Compute circle sizes in the same scale as altitude
    sun_radius = sun_angular_size / 2
    moon_radius = moon_angular_size / 2
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal', adjustable='datalim')
    
    # Horizon line
    ax.axhline(y=0, color='black', linewidth=2)
    
    # Draw sun and moon as filled circles with colored outlines
    ax.add_patch(plt.Circle((-2, sun_alt), sun_radius, color='orange', ec='darkorange', linewidth=2))
    ax.add_patch(plt.Circle((2, moon_alt), moon_radius, color='grey', ec='dimgray', linewidth=2))
    
    # Draw KIR1 and KIR2 red border lines
    border_altitude = 2 if kriteria == "KIR1" else 3
    arc_width = 6 if kriteria == "KIR1" else 12.8
    elongation_value = 3 if kriteria == "KIR1" else 6.4
    
    # Draw the red border line dynamically
    def update_border():
        xlim = ax.get_xlim()
        left_segment = np.linspace(xlim[0], -2 - sun_radius, 100)
        right_segment = np.linspace(2 + sun_radius, xlim[1], 100)

        border_line_left.set_xdata(left_segment)
        border_line_left.set_ydata([border_altitude] * len(left_segment))
        border_line_right.set_xdata(right_segment)
        border_line_right.set_ydata([border_altitude] * len(right_segment))
    
    # Initialize red border line objects
    border_line_left, = ax.plot([], [], 'r--', linewidth=1, label=f"Had Altitud ({border_altitude}°)")
    border_line_right, = ax.plot([], [], 'r--', linewidth=1)

    # Initial border line drawing
    update_border()
    
    # Draw elongation arc
    arc = Arc((-2, sun_alt), width=arc_width, height=arc_width, theta1=0, theta2=180, color='red', linestyle='dashed', linewidth=1, label=f'Had Elongasi ({elongation_value}°)')
    ax.add_patch(arc)
    
    # Labels
    ax.text(-2, sun_alt + sun_radius + 0.5, f"Matahari\n{sun_alt:.2f}°", ha='center', fontsize=10, weight='bold', color='black')
    ax.text(2, moon_alt + moon_radius + 0.5, f"Bulan\n{moon_alt:.2f}°", ha='center', fontsize=10, weight='bold', color='black')
    
    # Adjust axis
    ax.set_ylim(0, max(sun_alt, moon_alt) + 5)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Add title and location details
    location_str = f"{location_label}\n(Lat: {latitude}°, Long: {longitude}°, Elev: {elevation}m)"
    ax.set_title(f"Kedudukan Matahari dan Bulan\nTarikh: {date}  Masa: {hour:02d}:{minute:02d}\n{location_str}")
    
    # Enable zoom and pan functionality
    def on_scroll(event):
        scale_factor = 1.2 if event.step > 0 else 0.8
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ax.set_xlim([x * scale_factor for x in xlim])
        ax.set_ylim([y * scale_factor for y in ylim])

        update_border()  # Update red border dynamically
        fig.canvas.draw()
    
    def on_press(event):
        if event.button == 1:
            ax._drag_start = (event.xdata, event.ydata)
    
    def on_motion(event):
        if event.button == 1 and hasattr(ax, '_drag_start'):
            dx = event.xdata - ax._drag_start[0]
            dy = event.ydata - ax._drag_start[1]
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            ax.set_xlim([x - dx for x in xlim])
            ax.set_ylim([y - dy for y in ylim])
            ax._drag_start = (event.xdata, event.ydata)

            update_border()  # Update red border dynamically
            fig.canvas.draw()
    
    fig.canvas.mpl_connect('scroll_event', on_scroll)
    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('motion_notify_event', on_motion)
    
    plt.legend()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Melakar kedudukan Matahari dan Bulan di horizon.")
    parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")
    parser.add_argument("--location", default="bp", help="Location name from database/location.txt")
    parser.add_argument("--latitude", type=float, help="Latitude in degrees")
    parser.add_argument("--longitude", type=float, help="Longitude in degrees")
    parser.add_argument("--elevation", type=float, help="Elevation in meters")
    parser.add_argument("--timezone", default="Asia/Kuala_Lumpur", help="Time zone (e.g., Asia/Kuala_Lumpur)")
    parser.add_argument("--kriteria", choices=["KIR1", "KIR2"], default="KIR2", help="Kriteria Imkanur Rukyah")
    parser.add_argument("--time", help="Time in HHMM format (optional, defaults to when full sun is below horizon)")
    
    args = parser.parse_args()
    
    if args.location:
        args.latitude, args.longitude, args.elevation, args.timezone, location_label = load_location(args.location)
    elif not all([args.latitude, args.longitude, args.elevation, args.timezone]):
        raise ValueError("Either provide --location or all of --latitude, --longitude, --elevation, and --timezone")
    else:
        location_label = "Custom Location"
    
    plot_sun_moon(args.date, args.latitude, args.longitude, args.elevation, args.timezone, location_label, args.kriteria, args.time)
