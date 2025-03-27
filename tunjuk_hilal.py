import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from matplotlib.patches import Wedge
from matplotlib.widgets import RadioButtons
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
    #year, month, day = map(int, date.split('-'))
    year, month, day = int(date[:4]), int(date[4:6]), int(date[6:])
    
    if time:
        hour, minute = int(time[:2]), int(time[2:])
    else:
        _, sunset_time = sunrise_sunset_local(location, timezone, year=year, month=month, day=day)
        hour, minute = sunset_time.hour, sunset_time.minute
    
    sun_alt, _, _ = sun_position_time_local(location, timezone, year=year, month=month, day=day, hour=hour, minute=minute, second=0)
    moon_alt, _, _ = moon_position_time_local(location, timezone, year=year, month=month, day=day, hour=hour, minute=minute, second=0)
    
    sun_radius, moon_radius = 0.265, 0.25
    scale_factor = 1  # Adjust scale for better visualization
    
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal', adjustable='datalim')
    ax.axhline(y=0, color='black', linewidth=2)
    
    sun_circle = plt.Circle((-2, sun_alt), sun_radius, color='orange', ec='darkorange', linewidth=2)
    moon_circle = plt.Circle((2, moon_alt), moon_radius, color='grey', ec='dimgray', linewidth=2)
    ax.add_patch(sun_circle)
    ax.add_patch(moon_circle)
    
    sun_label = ax.text(-2, sun_alt - sun_radius - 0.5, f"Sun\n{sun_alt:.2f}°", ha='center', fontsize=10, weight='bold', color='black')
    moon_label = ax.text(2, moon_alt - moon_radius - 0.5, f"Moon\n{moon_alt:.2f}°", ha='center', fontsize=10, weight='bold', color='black')
        
    def update_labels():
        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        sun_label.set_visible(xlim[0] < -2 < xlim[1] and ylim[0] < sun_alt < ylim[1])
        moon_label.set_visible(xlim[0] < 2 < xlim[1] and ylim[0] < moon_alt < ylim[1])
        fig.canvas.draw()
    
    def update_plot(kriteria):
        update_labels()
        ax.clear()
        global sun_label, moon_label
        #sun_label = ax.text(-2, sun_alt + sun_radius + 0.5, f"Matahari\n{sun_alt:.2f}°", ha='center', fontsize=10, weight='bold', color='black', gid='sun_label')
        #moon_label = ax.text(2, moon_alt + moon_radius + 0.5, f"Bulan\n{moon_alt:.2f}°", ha='center', fontsize=10, weight='bold', color='black', gid='moon_label')
        #sun_label.set_text(f"Matahari\n{sun_alt:.2f}°")
        #moon_label.set_text(f"Bulan\n{moon_alt:.2f}°")
        sun_label = ax.text(-2, sun_alt + sun_radius + 0.2, f"Matahari", ha='center', fontsize=10, weight='bold', color='black', gid='sun_label')
        moon_label = ax.text(2, moon_alt + moon_radius + 0.2, f"Bulan", ha='center', fontsize=10, weight='bold', color='black', gid='moon_label')
        sun_label.set_text(f"Matahari")
        moon_label.set_text(f"Bulan")
        ax.add_artist(sun_label)
        ax.add_artist(moon_label)
        ax.axhline(y=0, color='black', linewidth=2)
        ax.add_patch(plt.Circle((-2, sun_alt), sun_radius, color='orange', ec='darkorange', linewidth=2))
        ax.add_patch(plt.Circle((2, moon_alt), moon_radius, color='grey', ec='dimgray', linewidth=2))
        
        if kriteria == "KIR1":
            border_altitude, arc_width, elongation_value = 2, 6, 3
        elif kriteria == "KIR2":
            border_altitude, arc_width, elongation_value = 3, 12.8, 6.4
        else:
            border_altitude, arc_width, elongation_value = None, None, None
        
        if kriteria in ["KIR1", "KIR2"]:
            ax.axhline(y=border_altitude, color='#FFABAB', linestyle='dotted', linewidth=1, label=f"Had Altitud ({border_altitude}°)")
            arc = Arc((-2, sun_alt), width=arc_width, height=arc_width, theta1=0, theta2=180, color='#FFABAB', linestyle='dotted', linewidth=1, label=f'Had Elongasi ({elongation_value}°)')
            ax.add_patch(arc)
        
        # Sun circle
        sun_x, sun_y = -2, sun_alt * scale_factor
        sun_circle = plt.Circle((sun_x, sun_y), sun_radius * scale_factor, color='orange', ec='darkorange', linewidth=2)
        ax.add_patch(sun_circle)

        # Set horizon border altitude shading
        kir_altitudes = {"KIR0": 0, "KIR1": 2, "KIR2": 3}
        border_altitude = kir_altitudes.get(kriteria, 0)
        ax.axhspan(0, border_altitude * scale_factor, xmin=0, xmax=1, color='#FFABAB', alpha=0.2, zorder=-5)

        # Glow effect around the sun
        kir_glow = {"KIR0": 0, "KIR1": 3, "KIR2": 6.4}
        glow_radius = kir_glow.get(kriteria, 0) * scale_factor
        for radius in np.linspace(sun_radius * scale_factor, glow_radius, 10):
            top_of_glow = sun_y + radius
            if top_of_glow > 0:
                start_angle = np.degrees(np.arccos(np.clip(-sun_y / radius, -1, 1)))
                visible_glow = Wedge((sun_x, sun_y), radius, 90 - start_angle, 90 + start_angle, color='#FFABAB', alpha=0.15, zorder=-1)
                ax.add_patch(visible_glow)
    
        ax.set_ylim(0, max(sun_alt, moon_alt) + 5)
        ax.set_xticks([])
        ax.set_yticks([])

        # Define Malay month names
        malay_months = {
            1: "Jan", 2: "Feb", 3: "Mac", 4: "Apr", 5: "Mei", 6: "Jun",
            7: "Jul", 8: "Ogo", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Dis"
        }

        # Get the Malay month name
        month_name = malay_months[month]

        # Convert hour to 12-hour format
        hour_12 = hour % 12 or 12
        am_pm = "AM" if hour < 12 else "PM"

        ax.set_title(f"Kedudukan Matahari dan Bulan\nTarikh: {day} {month_name} {year}  Masa: {hour_12}:{minute:02d} {am_pm}\n{location_label}\nLatitude: {latitude}°  Longitude: {longitude}°  Elevation: {elevation}m", pad=20)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=True)
        fig.text(0.52, 0.07, "Ini merupakan janaan dari python menggunakan pengiraan ahc\nbagi menentukan kedudukan matahari dan bulan bagi melihat kemungkinan kenampakan hilal", ha='center', fontsize=10, style='italic', color='gray')
        update_labels()
        fig.canvas.draw()
    
    ax_button = plt.axes([0.85, 0.75, 0.12, 0.15])
    radio = RadioButtons(ax_button, ('KIR0', 'KIR1', 'KIR2'))
    radio.set_active(2)
    radio.on_clicked(update_plot)
    
    update_plot("KIR2")
    
    def on_scroll(event):
        scale_factor = 0.8 if event.step > 0 else 1.2
        ax.set_xlim([x * scale_factor for x in ax.get_xlim()])
        ax.set_ylim([y * scale_factor for y in ax.get_ylim()])
        update_labels()
        fig.canvas.draw()
    
    fig.canvas.mpl_connect('scroll_event', on_scroll)
    def on_press(event):
        if event.button == 1:
            ax._drag_start = (event.xdata, event.ydata)
    
    def on_motion(event):
        if event.button == 1 and hasattr(ax, '_drag_start'):
            dx = event.xdata - ax._drag_start[0]
            dy = event.ydata - ax._drag_start[1]
            ax.set_xlim([x - dx for x in ax.get_xlim()])
            ax.set_ylim([y - dy for y in ax.get_ylim()])
            ax._drag_start = (event.xdata, event.ydata)
            update_labels()
            fig.canvas.draw()
    
    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('motion_notify_event', on_motion)
    
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYYMMDD")
    parser.add_argument("--location", default="bp")
    parser.add_argument("--latitude", type=float)
    parser.add_argument("--longitude", type=float)
    parser.add_argument("--elevation", type=float)
    parser.add_argument("--timezone", default="Asia/Kuala_Lumpur")
    parser.add_argument("--kriteria", choices=["KIR0", "KIR1", "KIR2"], default="KIR2")
    parser.add_argument("--time", help="HHMM")
    
    args = parser.parse_args()
    if args.location:
        args.latitude, args.longitude, args.elevation, args.timezone, location_label = load_location(args.location)
    elif not all([args.latitude, args.longitude, args.elevation, args.timezone]):
        raise ValueError("Provide either --location or all --latitude, --longitude, --elevation, and --timezone")
    else:
        location_label = "Custom Location"
    
    plot_sun_moon(args.date, args.latitude, args.longitude, args.elevation, args.timezone, location_label, args.kriteria, args.time)
