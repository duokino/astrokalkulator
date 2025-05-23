import numpy as np 
from skyfield import api
from skyfield import almanac
from datetime import datetime
from datetime import timedelta
from calendar import monthrange
from skyfield.units import Angle
import os

from .sunmoon import *

__all__ = ["get_map_moon_alt_atsunset", "get_map_moon_elongation_atsunset", "get_map_moon_geocentric_elongation_atsunset", 
			"get_map_moon_width_atsunset", "crescent_data", "get_map_moon_arcv_atsunset", "get_map_moon_properties_atsunset"]

global ts, ephem
# Load ephemeris data
ts = api.load.timescale()

# Find the latest .bsp file
bsp_files = [f for f in os.listdir('database') if f.endswith('.bsp')]
latest_bsp = max(bsp_files) if bsp_files else 'de421.bsp'  # Fallback to de421.bsp if none found
ephem = api.load_file(f'database/{latest_bsp}')


def get_map_moon_alt_atsunset(year, month, day, min_lat=-60.0, max_lat=70.0, min_long=-180.0, max_long=180.0, factor=0.5):
	import sys

	min_lat1, max_lat1, min_long1, max_long1 = -90, 90, -180, 180

	nlat = int(factor*((max_lat1-min_lat1)+1))
	nlong = int(factor*((max_long1-min_long1)+1))
	grid_lat = np.linspace(min_lat1, max_lat1, nlat)
	grid_long = np.linspace(min_long1, max_long1, nlong)

	map_moon_alt = np.zeros((nlat,nlong))
	count = 0
	for yy in range(0,nlat-1):
		for xx in range(0,nlong-1):
			if grid_lat[yy]>=min_lat and grid_lat[yy]<=max_lat and grid_long[xx]>=min_long and grid_long[xx]<=max_long:
				lat1 = 0.5*(grid_lat[yy] + grid_lat[yy+1])
				long1 = 0.5*(grid_long[xx] + grid_long[xx+1])
				location = set_location(lat1, long1, 0)
				sunrise, sunset = sunrise_sunset_utc(location, year=year, month=month, day=day)
				if sunset is None:
					moon_alt = -999
				else:
					moon_alt, moon_az, dist = moon_position_time_utc(location, utc_datetime=sunset)
				map_moon_alt[yy][xx] = moon_alt
			else:
				map_moon_alt[yy][xx] = float('nan')

			count = count + 1
			sys.stdout.write('\r')
			sys.stdout.write('progress: %d of %d (%d%%)' % (count,(nlat-1)*(nlong-1),count*100/(nlong-1)/(nlat-1)))
			sys.stdout.flush()

	return map_moon_alt


def get_map_moon_arcv_atsunset(year, month, day, min_lat=-60.0, max_lat=70.0, min_long=-180.0, max_long=180.0, factor=0.5):
	import sys

	min_lat1, max_lat1, min_long1, max_long1 = -90, 90, -180, 180

	nlat = int(factor*((max_lat1-min_lat1)+1))
	nlong = int(factor*((max_long1-min_long1)+1))
	grid_lat = np.linspace(min_lat1, max_lat1, nlat)
	grid_long = np.linspace(min_long1, max_long1, nlong)

	map_moon_arcv = np.zeros((nlat,nlong))
	count = 0
	for yy in range(0,nlat-1):
		for xx in range(0,nlong-1):
			if grid_lat[yy]>=min_lat and grid_lat[yy]<=max_lat and grid_long[xx]>=min_long and grid_long[xx]<=max_long:
				lat1 = 0.5*(grid_lat[yy] + grid_lat[yy+1])
				long1 = 0.5*(grid_long[xx] + grid_long[xx+1])
				location = set_location(lat1, long1, 0)
				sunrise, sunset = sunrise_sunset_utc(location, year=year, month=month, day=day)
				if sunset is None:
					moon_arcv = -999
				else:
					moon_alt, moon_az, dist = moon_position_time_utc(location, utc_datetime=sunset)
					sun_alt, sun_az, dist = sun_position_time_utc(location, utc_datetime=sunset)
					moon_arcv = moon_alt - sun_alt

				map_moon_arcv[yy][xx] = moon_arcv
			else:
				map_moon_arcv[yy][xx] = float('nan')

			count = count + 1
			sys.stdout.write('\r')
			sys.stdout.write('progress: %d of %d (%d%%)' % (count,(nlat-1)*(nlong-1),count*100/(nlong-1)/(nlat-1)))
			sys.stdout.flush()

	return map_moon_arcv	


def get_map_moon_elongation_atsunset(year, month, day, min_lat=-60.0, max_lat=70.0, min_long=-180.0, max_long=180.0, factor=0.5):
	import sys

	min_lat1, max_lat1, min_long1, max_long1 = -90, 90, -180, 180

	nlat = int(factor*((max_lat1-min_lat1)+1))
	nlong = int(factor*((max_long1-min_long1)+1))
	grid_lat = np.linspace(min_lat1, max_lat1, nlat)
	grid_long = np.linspace(min_long1, max_long1, nlong)

	map_moon_elongation = np.zeros((nlat,nlong))
	count = 0
	for yy in range(nlat-1):
		for xx in range(nlong-1):
			if grid_lat[yy]>=min_lat and grid_lat[yy]<=max_lat and grid_long[xx]>=min_long and grid_long[xx]<=max_long:
				lat1 = 0.5*(grid_lat[yy] + grid_lat[yy+1])
				long1 = 0.5*(grid_long[xx] + grid_long[xx+1])
				location = set_location(lat1, long1, 0)
				sunrise, sunset = sunrise_sunset_utc(location, year=year, month=month, day=day)
				if sunset is None:
					moon_elong = -999
				else:
					moon_elong = moon_elongation_time_utc(location=location, utc_datetime=sunset)
				map_moon_elongation[yy][xx] = moon_elong
			else:
				map_moon_elongation[yy][xx] = float('nan')

			count = count + 1
			sys.stdout.write('\r')
			sys.stdout.write('progress: %d of %d (%d%%)' % (count,(nlat-1)*(nlong-1),count*100/(nlong-1)/(nlat-1)))
			sys.stdout.flush()

	return map_moon_elongation


def get_map_moon_geocentric_elongation_atsunset(year, month, day, min_lat=-60.0, max_lat=70.0, min_long=-180.0, max_long=180.0, factor=0.5):
	import sys

	min_lat1, max_lat1, min_long1, max_long1 = -90, 90, -180, 180

	nlat = int(factor*((max_lat1-min_lat1)+1))
	nlong = int(factor*((max_long1-min_long1)+1))
	grid_lat = np.linspace(min_lat1, max_lat1, nlat)
	grid_long = np.linspace(min_long1, max_long1, nlong)

	map_moon_elongation = np.zeros((nlat,nlong))
	count = 0
	for yy in range(nlat-1):
		for xx in range(nlong-1):
			if grid_lat[yy]>=min_lat and grid_lat[yy]<=max_lat and grid_long[xx]>=min_long and grid_long[xx]<=max_long:
				lat1 = 0.5*(grid_lat[yy] + grid_lat[yy+1])
				long1 = 0.5*(grid_long[xx] + grid_long[xx+1])
				location = set_location(lat1, long1, 0)
				sunrise, sunset = sunrise_sunset_utc(location, year=year, month=month, day=day)
				if sunset is None:
					moon_elong = -999
				else:
					moon_elong = moon_elongation_time_utc(utc_datetime=sunset)
				map_moon_elongation[yy][xx] = moon_elong
			else:
				map_moon_elongation[yy][xx] = float('nan')

			count = count + 1
			sys.stdout.write('\r')
			sys.stdout.write('progress: %d of %d (%d%%)' % (count,(nlat-1)*(nlong-1),count*100/(nlong-1)/(nlat-1)))
			sys.stdout.flush()

	return map_moon_elongation


def get_map_moon_width_atsunset(year, month, day, min_lat=-60.0, max_lat=70.0, min_long=-180.0, max_long=180.0, factor=0.5):
	import sys

	min_lat1, max_lat1, min_long1, max_long1 = -90, 90, -180, 180

	nlat = int(factor*((max_lat1-min_lat1)+1))
	nlong = int(factor*((max_long1-min_long1)+1))
	grid_lat = np.linspace(min_lat1, max_lat1, nlat)
	grid_long = np.linspace(min_long1, max_long1, nlong)

	map_moon_width = np.zeros((nlat,nlong))
	count = 0
	for yy in range(nlat-1):
		for xx in range(nlong-1):
			if grid_lat[yy]>=min_lat and grid_lat[yy]<=max_lat and grid_long[xx]>=min_long and grid_long[xx]<=max_long:
				lat1 = 0.5*(grid_lat[yy] + grid_lat[yy+1])
				long1 = 0.5*(grid_long[xx] + grid_long[xx+1])
				location = set_location(lat1, long1, 0)
				sunrise, sunset = sunrise_sunset_utc(location, year=year, month=month, day=day)
				if sunset is None:
					moon_width = -999
				else:
					illumination, moon_width, parallax, SD = moon_illumination_width_utc(location=location, utc_datetime=sunset)

				map_moon_width[yy][xx] = moon_width
			else:
				map_moon_width[yy][xx] = float('nan')

			count = count + 1
			sys.stdout.write('\r')
			sys.stdout.write('progress: %d of %d (%d%%)' % (count,(nlat-1)*(nlong-1),count*100/(nlong-1)/(nlat-1)))
			sys.stdout.flush()

	return map_moon_width


def get_map_moon_properties_atsunset(year, month, day, ijtima_utc, plus_1day=True, min_lat=-60.0, max_lat=70.0, min_long=-180.0, max_long=180.0, factor=0.5):
	import sys

	min_lat1, max_lat1, min_long1, max_long1 = -90, 90, -180, 180

	nlat = int(factor*((max_lat1-min_lat1)+1))
	nlong = int(factor*((max_long1-min_long1)+1))
	grid_lat = np.linspace(min_lat1, max_lat1, nlat)
	grid_long = np.linspace(min_long1, max_long1, nlong)

	map_moon_alt = np.zeros((nlat,nlong))
	map_moon_arcv = np.zeros((nlat,nlong))
	map_moon_elong = np.zeros((nlat,nlong))
	map_moon_elong_geo = np.zeros((nlat,nlong))
	map_moon_width = np.zeros((nlat,nlong))
	map_moon_age_utc_seconds = np.zeros((nlat,nlong))
	count = 0
	for yy in range(0,nlat-1):
		for xx in range(0,nlong-1):
			if grid_lat[yy]>=min_lat and grid_lat[yy]<=max_lat and grid_long[xx]>=min_long and grid_long[xx]<=max_long:
				lat1 = 0.5*(grid_lat[yy] + grid_lat[yy+1])
				long1 = 0.5*(grid_long[xx] + grid_long[xx+1])
				location = set_location(lat1, long1, 0)
				sunrise, sunset = sunrise_sunset_utc(location, year=year, month=month, day=day)
				if sunset is None:
					moon_alt, moon_arcv, moon_elong, moon_elong_geo, moon_width, moon_age_utc_seconds = float('nan'), float('nan'), float('nan'), float('nan'), float('nan'), float('nan')
				else:
					moon_alt, moon_az, dist = moon_position_time_utc(location, utc_datetime=sunset)
					sun_alt, sun_az, dist = sun_position_time_utc(location, utc_datetime=sunset)
					moon_arcv = moon_alt - sun_alt
					moon_elong = moon_elongation_time_utc(location=location, utc_datetime=sunset)
					moon_elong_geo = moon_elongation_time_utc(utc_datetime=sunset)
					illumination, moon_width, parallax, SD = moon_illumination_width_utc(location=location, utc_datetime=sunset)
					moon_age_utc_seconds = calc_timedelta_seconds(ijtima_utc, sunset)

				map_moon_alt[yy][xx] = moon_alt
				map_moon_arcv[yy][xx] = moon_arcv
				map_moon_elong[yy][xx] = moon_elong
				map_moon_elong_geo[yy][xx] = moon_elong_geo
				map_moon_width[yy][xx] = moon_width
				map_moon_age_utc_seconds[yy][xx] = moon_age_utc_seconds
			else:
				map_moon_alt[yy][xx] = float('nan')
				map_moon_arcv[yy][xx] = float('nan')
				map_moon_elong[yy][xx] = float('nan')
				map_moon_elong_geo[yy][xx] = float('nan')
				map_moon_width[yy][xx] = float('nan')
				map_moon_age_utc_seconds[yy][xx] = float('nan')

			count = count + 1
			sys.stdout.write('\r')
			sys.stdout.write('progress: %d of %d (%d%%)' % (count,(nlat-1)*(nlong-1),count*100/(nlong-1)/(nlat-1)))
			sys.stdout.flush()

	map_moon_properties = {}
	map_moon_properties['alt'] = map_moon_alt
	map_moon_properties['arcv'] = map_moon_arcv
	map_moon_properties['elong'] = map_moon_elong
	map_moon_properties['elong_geo'] = map_moon_elong_geo
	map_moon_properties['width'] = map_moon_width
	map_moon_properties['age_utc'] = map_moon_age_utc_seconds

	if plus_1day == True:
		map_moon_alt = np.zeros((nlat,nlong))
		map_moon_arcv = np.zeros((nlat,nlong))
		map_moon_elong = np.zeros((nlat,nlong))
		map_moon_elong_geo = np.zeros((nlat,nlong))
		map_moon_width = np.zeros((nlat,nlong))
		map_moon_age_utc_seconds = np.zeros((nlat,nlong))
		count = 0
		for yy in range(0,nlat-1):
			for xx in range(0,nlong-1):
				if grid_lat[yy]>=min_lat and grid_lat[yy]<=max_lat and grid_long[xx]>=min_long and grid_long[xx]<=max_long:
					lat1 = 0.5*(grid_lat[yy] + grid_lat[yy+1])
					long1 = 0.5*(grid_long[xx] + grid_long[xx+1])
					location = set_location(lat1, long1, 0)

					ijtima_utc_plus1 = ijtima_utc + timedelta(days=1)
					sunrise, sunset = sunrise_sunset_utc(location, year=ijtima_utc_plus1.year, month=ijtima_utc_plus1.month, day=ijtima_utc_plus1.day)   ##############

					if sunset is None:
						moon_alt, moon_arcv, moon_elong, moon_elong_geo, moon_width, moon_age_utc_seconds = float('nan'), float('nan'), float('nan'), float('nan'), float('nan'), float('nan')
					else:
						moon_alt, moon_az, dist = moon_position_time_utc(location, utc_datetime=sunset)
						sun_alt, sun_az, dist = sun_position_time_utc(location, utc_datetime=sunset)
						moon_arcv = moon_alt - sun_alt
						moon_elong = moon_elongation_time_utc(location=location, utc_datetime=sunset)
						moon_elong_geo = moon_elongation_time_utc(utc_datetime=sunset)
						illumination, moon_width, parallax, SD = moon_illumination_width_utc(location=location, utc_datetime=sunset)
						moon_age_utc_seconds = calc_timedelta_seconds(ijtima_utc, sunset)

					map_moon_alt[yy][xx] = moon_alt
					map_moon_arcv[yy][xx] = moon_arcv
					map_moon_elong[yy][xx] = moon_elong
					map_moon_elong_geo[yy][xx] = moon_elong_geo
					map_moon_width[yy][xx] = moon_width
					map_moon_age_utc_seconds[yy][xx] = moon_age_utc_seconds
				else:
					map_moon_alt[yy][xx] = float('nan')
					map_moon_arcv[yy][xx] = float('nan')
					map_moon_elong[yy][xx] = float('nan')
					map_moon_elong_geo[yy][xx] = float('nan')
					map_moon_width[yy][xx] = float('nan')
					map_moon_age_utc_seconds[yy][xx] = float('nan')

				count = count + 1
				sys.stdout.write('\r')
				sys.stdout.write('progress: %d of %d (%d%%)' % (count,(nlat-1)*(nlong-1),count*100/(nlong-1)/(nlat-1)))
				sys.stdout.flush()

		map_moon_properties['alt1'] = map_moon_alt
		map_moon_properties['arcv1'] = map_moon_arcv
		map_moon_properties['elong1'] = map_moon_elong
		map_moon_properties['elong_geo1'] = map_moon_elong_geo
		map_moon_properties['width1'] = map_moon_width
		map_moon_properties['age_utc1'] = map_moon_age_utc_seconds

	return map_moon_properties


def crescent_data(hijri_year, hijri_month, latitude, longitude, elevation, time_zone_str, loc_name=None, delta_day=0,
					temperature_C=10.0, pressure_mbar=1030.0, sun_radius_degrees=0.2665, moon_radius_degrees=0.2575):

	# get names of the hijri months in string
	hijri_months_string = list_hijri_months()
	
	# get location
	location = set_location(latitude, longitude, elevation)

	# get conjuction time
	ijtima_local = newmoon_hijri_month_local_time(hijri_year, hijri_month, time_zone_str)
	ijtima_utc = newmoon_hijri_month_utc(hijri_year, hijri_month)

	# adjust day of calculation
	calc_ijtima_local = ijtima_local + timedelta(days=delta_day)

	# get local time of sunset
	sunrise_local, sunset_local = sunrise_sunset_local(location, time_zone_str, year=calc_ijtima_local.year, month=calc_ijtima_local.month, day=calc_ijtima_local.day, 
													temperature_C=temperature_C, pressure_mbar=pressure_mbar, radius_degrees=sun_radius_degrees)

	# get local time of moonset
	moonrise_local, moonset_local = moonrise_moonset_local(location, time_zone_str, year=calc_ijtima_local.year, month=calc_ijtima_local.month, day=calc_ijtima_local.day, 
													temperature_C=temperature_C, pressure_mbar=pressure_mbar, radius_degrees=moon_radius_degrees)


	# get sun position at sunset
	sun_alt, sun_az, sun_dist = sun_position_time_local(location, time_zone_str, local_datetime=sunset_local, temperature_C=temperature_C, pressure_mbar=pressure_mbar)

	# get moon position at sunset
	moon_alt, moon_az, moon_dist = moon_position_time_local(location, time_zone_str, local_datetime=sunset_local, temperature_C=temperature_C, pressure_mbar=pressure_mbar)

	# get moon elongation at sunset
	moon_elong = moon_elongation_time_local(time_zone_str, location=location, local_datetime=sunset_local)
	moon_elong_geo = moon_elongation_time_local(time_zone_str, local_datetime=sunset_local)

	# get moon illumination, width, and horizontal parallax
	illumination, width, parallax, SD = moon_illumination_width_local(time_zone_str, location=location, local_datetime=sunset_local)

	# get lag time and the hilal's age 
	moon_lag_time = calc_timedelta_seconds(sunset_local, moonset_local)
	moon_age = calc_timedelta_seconds(ijtima_local, sunset_local)

	# get time differnce between UTC and local
	sunset_utc = convert_localtime_to_utc(time_zone_str, local_datetime=sunset_local)
	delta_time_tz = calc_timedelta_seconds(datetime(ijtima_utc.year, ijtima_utc.month, ijtima_utc.day, ijtima_utc.hour, ijtima_utc.minute, ijtima_utc.second), datetime(ijtima_local.year, ijtima_local.month, ijtima_local.day, ijtima_local.hour, ijtima_local.minute, ijtima_local.second))
	
	#print ('\n')
	#print ('\n')
	print ('\n')
	print ('                       Data Hilal bagi %s %d' % (hijri_months_string[int(hijri_month)-1],hijri_year))
	print ("          menggunakan metod pengiraan Accurate Hijri Calculator (AHC)")
	print ('                                    @duokino\n')
	#print ('- Pengiraan dibuat semasa matahari terbenam pada jam %02d:%02d:%02d pada tarikh %d-%d-%d' % (sunset_local.hour,sunset_local.minute,sunset_local.second,calc_ijtima_local.day,calc_ijtima_local.month,calc_ijtima_local.year))
	print ('  Pengiraan dibuat semasa matahari terbenam pada jam %02d:%02d:%02d pada tarikh %d-%d-%d' % (sunset_local.hour,sunset_local.minute,sunset_local.second,sunset_local.day,sunset_local.month,sunset_local.year))
	print ('')
	if loc_name is None:
		print ('  Lokasi: ')
	else:
		print ('  Lokasi: '+loc_name)
	print ('')
	print ('   - Lat: '+print_angle(latitude)+'  Long: '+print_angle(longitude)+'  Elev: %.2f m' % elevation)
	if delta_time_tz<0:
		print ('   - Time zone: '+time_zone_str+' '+print_timedelta_tz(delta_time_tz))
	else:
		print ('   - Time zone: '+time_zone_str+' +'+print_timedelta_tz(delta_time_tz))
	#print ('   - Keadaan Pembiasan Atmosfera => Suhu: %d °C  Tekanan: %d mb' % (temperature_C, pressure_mbar))
	print ('\n============================================================================================\n')
	print ('  Waktu Ijtimak: %d-%d-%d %02d:%02d:%02d (Waktu Tempatan) atau %d-%d-%d %02d:%02d:%02d UTC' % (ijtima_local.day,ijtima_local.month,ijtima_local.year,ijtima_local.hour,ijtima_local.minute,ijtima_local.second,ijtima_utc.day,ijtima_utc.month,ijtima_utc.year,ijtima_utc.hour,ijtima_utc.minute,ijtima_utc.second))
	print ('\n  - Waktu Matahari terbenam: %02d:%02d:%02d          - Waktu Bulan terbenam        : %02d:%02d:%02d' % (sunset_local.hour,sunset_local.minute,sunset_local.second, moonset_local.hour,moonset_local.minute,moonset_local.second))
	print ('  - Altitude Matahari      : '+print_angle(sun_alt)+'       - Umur Bulan                  : '+print_timedelta(moon_age))
	print ('  - Azimut Matahari        : '+print_angle(sun_az)+'      - Tempoh mencerap Bulan       : '+print_timedelta(moon_lag_time))
	print ('  - Ketebalan Hilal        : '+print_angle(width)+'        - Altitud Bulan               : '+print_angle(moon_alt))
	print ('  - Iluminasi Bulan        : %.2f' % illumination+' %            - Azimut Bulan                : '+print_angle(moon_az))
	print ('  - Jarak Bulan            : %.2f' % moon_dist+' km      - Elongasi Bulan (topocentric): '+print_angle(moon_elong))
	print ('  - Semi-diameter Bulan    : '+print_angle(SD)+'        - Elongasi Bulan (geocentric) : '+print_angle(moon_elong_geo))
	print ('  - Parallax horizon Bulan : '+print_angle(parallax))
	print ('')
	print ('  *Semua data berdasarkan keadaan tempatan di lokasi pemerhati')
	#print ('')












