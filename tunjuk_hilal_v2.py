import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Wedge
from matplotlib.widgets import CheckButtons
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


def plot_sun_moon(date, latitude, longitude, elevation, timezone, location_label, time):

    location = set_location(latitude, longitude, elevation)
    year, month, day = int(date[:4]), int(date[4:6]), int(date[6:])

    if time:
        hour, minute = int(time[:2]), int(time[2:])
    else:
        _, sunset_time = sunrise_sunset_local(location, timezone,
                                              year=year, month=month, day=day)
        hour, minute = sunset_time.hour, sunset_time.minute

    sun_alt, _, _ = sun_position_time_local(location, timezone,
                                            year=year, month=month, day=day,
                                            hour=hour, minute=minute, second=0)

    moon_alt, _, _ = moon_position_time_local(location, timezone,
                                              year=year, month=month, day=day,
                                              hour=hour, minute=minute, second=0)

    sun_radius, moon_radius = 0.265, 0.25

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal', adjustable='datalim')

    kir_status = {
        "KIR1": False,
        "KIR2": True
    }

    def draw_kir(kir_type):

        if kir_type == "KIR1":
            color_border, border_altitude, arc_width, elongation_value = '#E77577', 2, 6, 3
        elif kir_type == "KIR2":
            color_border, border_altitude, arc_width, elongation_value = '#FFBF65', 3, 12.8, 6.4
        else:
            return

        ax.axhline(y=border_altitude,
                   color=color_border,
                   linestyle='dotted',
                   linewidth=1,
                   label=f"{kir_type} Alt ({border_altitude}°)")

        arc = Arc((-2, sun_alt),
                  width=arc_width,
                  height=arc_width,
                  theta1=0,
                  theta2=180,
                  color=color_border,
                  linestyle='dotted',
                  linewidth=1,
                  label=f"{kir_type} Elong ({elongation_value}°)")
        ax.add_patch(arc)

        ax.axhspan(0, border_altitude,
                   xmin=0, xmax=1,
                   color=color_border,
                   alpha=0.15,
                   zorder=-5)

        sun_x, sun_y = -2, sun_alt
        for radius in np.linspace(sun_radius, elongation_value, 10):
            if sun_y + radius > 0:
                start_angle = np.degrees(
                    np.arccos(np.clip(-sun_y / radius, -1, 1))
                )
                glow = Wedge((sun_x, sun_y),
                             radius,
                             90 - start_angle,
                             90 + start_angle,
                             color=color_border,
                             alpha=0.1,
                             zorder=-1)
                ax.add_patch(glow)

    def redraw():

        current_xlim = ax.get_xlim()
        current_ylim = ax.get_ylim()

        ax.clear()
        ax.axhline(y=0, color='black', linewidth=2)

        ax.add_patch(plt.Circle((-2, sun_alt),
                                sun_radius,
                                color='orange',
                                ec='darkorange',
                                linewidth=2))

        ax.add_patch(plt.Circle((2, moon_alt),
                                moon_radius,
                                color='grey',
                                ec='dimgray',
                                linewidth=2))

        ax.text(-2, sun_alt + sun_radius + 0.2,
                "Matahari",
                ha='center',
                fontsize=10,
                weight='bold')

        ax.text(2, moon_alt + moon_radius + 0.2,
                "Bulan",
                ha='center',
                fontsize=10,
                weight='bold')

        for kir, active in kir_status.items():
            if active:
                draw_kir(kir)

        ax.set_xticks([])
        ax.set_yticks([])

        if current_xlim != (0.0, 1.0):
            ax.set_xlim(current_xlim)
            ax.set_ylim(current_ylim)
        else:
            ax.set_ylim(0, max(sun_alt, moon_alt) + 5)

        malay_months = {
            1: "Jan", 2: "Feb", 3: "Mac", 4: "Apr", 5: "Mei", 6: "Jun",
            7: "Jul", 8: "Ogo", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Dis"
        }

        month_name = malay_months[month]
        hour_12 = hour % 12 or 12
        am_pm = "AM" if hour < 12 else "PM"

        ax.set_title(
            f"Kedudukan Matahari dan Bulan\n"
            f"Tarikh: {day} {month_name} {year}  Masa: {hour_12}:{minute:02d} {am_pm}\n"
            f"{location_label}\n"
            f"Latitude: {latitude}°  Longitude: {longitude}°  Elevation: {elevation}m",
            pad=20
        )

        ax.legend(loc='upper center',
                  bbox_to_anchor=(0.5, 1.0),
                  ncol=2,
                  frameon=True)

        fig.canvas.draw_idle()

    def on_check(label):
        kir_status[label] = not kir_status[label]
        redraw()

    # ===== CHECK BUTTONS =====
    ax_check = plt.axes([0.83, 0.70, 0.15, 0.20])
    labels = ["KIR1", "KIR2"]
    visibility = [kir_status[l] for l in labels]
    check = CheckButtons(ax_check, labels, visibility)
    check.on_clicked(on_check)

    # ===== ZOOM FUNCTION =====
    def on_scroll(event):
        base_scale = 1.2
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()

        xdata = event.xdata
        ydata = event.ydata

        if xdata is None or ydata is None:
            return

        scale_factor = 1 / base_scale if event.step > 0 else base_scale

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

        ax.set_xlim([xdata - new_width * (1 - relx),
                     xdata + new_width * relx])
        ax.set_ylim([ydata - new_height * (1 - rely),
                     ydata + new_height * rely])

        fig.canvas.draw_idle()

    # ===== DRAG FUNCTION =====
    def on_press(event):
        if event.button == 1 and event.inaxes == ax:
            ax._drag_start = (event.xdata, event.ydata)

    def on_motion(event):
        if event.button == 1 and hasattr(ax, '_drag_start') and event.inaxes == ax:
            dx = event.xdata - ax._drag_start[0]
            dy = event.ydata - ax._drag_start[1]

            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            ax.set_xlim(cur_xlim[0] - dx, cur_xlim[1] - dx)
            ax.set_ylim(cur_ylim[0] - dy, cur_ylim[1] - dy)

            ax._drag_start = (event.xdata, event.ydata)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect('scroll_event', on_scroll)
    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('motion_notify_event', on_motion)

    redraw()
    plt.show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYYMMDD")
    parser.add_argument("--location", default="bp")
    parser.add_argument("--latitude", type=float)
    parser.add_argument("--longitude", type=float)
    parser.add_argument("--elevation", type=float)
    parser.add_argument("--timezone", default="Asia/Kuala_Lumpur")
    parser.add_argument("--time", help="HHMM")

    args = parser.parse_args()

    if args.location:
        args.latitude, args.longitude, args.elevation, args.timezone, location_label = load_location(args.location)
    elif not all([args.latitude, args.longitude, args.elevation, args.timezone]):
        raise ValueError("Provide either --location or all parameters")
    else:
        location_label = "Custom Location"

    plot_sun_moon(args.date,
                  args.latitude,
                  args.longitude,
                  args.elevation,
                  args.timezone,
                  location_label,
                  args.time)
