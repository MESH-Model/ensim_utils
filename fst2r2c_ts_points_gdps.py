#!/usr/bin/python

from os import path
from time import gmtime, strftime
from datetime import datetime
from dateutil import relativedelta as dt, tz, parser as dtparser
import numpy as np
import csv
import rpnpy.librmn.all as rmn
from ensim_utils import *
from fst2r2c_timeseries import *

# To load rpnpy:
# . s.ssmuse.dot ENV/py/2.7/rpnpy/2.0.4

na = []
la = []
lo = []
with open('station_locations.csv', 'rb') as f:
	reader = csv.reader(f)
	columns = next(reader)
	colmap = dict(zip(columns, range(len(columns))))
	for row in reader:
		na.append(row[colmap['Station']])
		la.append(row[colmap['Latitude']])
		lo.append(row[colmap['Longitude']])

LOCAL_TIME_ZONE = tz.gettz('UTC+03')
if (LOCAL_TIME_ZONE is None):
	print('ERROR: The time zone is not supported. The script cannot continue.')
	exit()
START_TIME = datetime(2012, 1, 1, tzinfo = LOCAL_TIME_ZONE)
STOP_BEFORE_TIME = datetime(2019, 1, 1, tzinfo = LOCAL_TIME_ZONE)
FST_PRODUCT = 'glbeta'
FST_RECORD_MINUTES = +180
if ((LOCAL_TIME_ZONE.utcoffset(START_TIME).total_seconds()/60.0) % FST_RECORD_MINUTES != 0):
	print('ERROR: Time-offset (%d minutes) is incompatible with time-stepping of files (%d minutes). The script cannot continue.' % ((LOCAL_TIME_ZONE.utcoffset(START_TIME).total_seconds()/60.0), FST_RECORD_MINUTES))
	exit()

# Initialize time loop.
# 180 minute stepping for GEM (GDPS).

UTC_STD_OFFSET = LOCAL_TIME_ZONE.utcoffset(START_TIME) - LOCAL_TIME_ZONE.dst(START_TIME)
FST_START_TIME = START_TIME.astimezone(tz.tzutc()) + LOCAL_TIME_ZONE.dst(START_TIME)
FST_STOP_BEFORE_TIME = STOP_BEFORE_TIME.astimezone(tz.tzutc()) + LOCAL_TIME_ZONE.dst(STOP_BEFORE_TIME)
FST_CURRENT_TIME = FST_START_TIME

# Fields.
PROCESS_FSTCONVFLD = []
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_temperature_linear_40m_K', fstnomvar = 'TT', AttributeName = 'Air_temperature_at_40m', AttributeUnits = 'K', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR, constadd = 273.16))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_temperature_linear_40m_dC', fstnomvar = 'TT', AttributeName = 'Air_temperature_at_40m', AttributeUnits = '\"degrees C\"', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_temperature_linear_2m_K', fstnomvar = 'TT', AttributeName = 'Air_temperature_at_2m', AttributeUnits = 'K', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR, constadd = 273.16))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_temperature_linear_2m_dC', fstnomvar = 'TT', AttributeName = 'Air_temperature_at_2m', AttributeUnits = '\"degrees C\"', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_specific_humidity_linear_40m', fstnomvar = 'HU', AttributeName = 'Specific_humidity_40m', AttributeUnits = '\"kg kg**-1\"', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_specific_humidity_linear_2m', fstnomvar = 'HU', AttributeName = 'Specific_humidity_2m', AttributeUnits = '\"kg kg**-1\"', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_pres_linear', fstnomvar = 'P0', AttributeName = 'Air_pressure_at_surface', AttributeUnits = 'Pa', intpopt = rmn.EZ_INTERP_LINEAR, constmul = 100.0))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_longwave_incoming_linear', fstnomvar = 'FI', AttributeName = 'Incoming_longwave_down_incident_at_surface', AttributeUnits = '\"W m**-2\"', intpopt = rmn.EZ_INTERP_LINEAR))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_shortwave_incoming_linear', fstnomvar = 'FB', AttributeName = 'Incoming_shortwave_down_incident_at_surface', AttributeUnits = '\"W m**-2\"', intpopt = rmn.EZ_INTERP_LINEAR))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_linear_40m', fstnomvar = 'UV', AttributeName = 'Wind_speed_at_40m', AttributeUnits = '\"m s**-1\"', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.5144444444444444444))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_linear_40m_knots', fstnomvar = 'UV', AttributeName = 'Wind_speed_at_40m', AttributeUnits = 'knots', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_winddir_linear_40m', fstnomvar = 'WD', AttributeName = 'Wind_direction_at_40m', AttributeUnits = 'degrees', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_u-component_linear_40m', fstnomvar = 'UU', AttributeName = 'Wind_speed_U-component_at_40m', AttributeUnits = '\"m s**-1\"', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.5144444444444444444))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_v-component_linear_40m', fstnomvar = 'VV', AttributeName = 'Wind_spped_V-component_at_40m', AttributeUnits = '\"m s**-1\"', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.5144444444444444444))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_linear_10m', fstnomvar = 'UV', AttributeName = 'Wind_speed_at_10m', AttributeUnits = '\"m s**-1\"', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.5144444444444444444))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_linear_10m_knots', fstnomvar = 'UV', AttributeName = 'Wind_speed_at_10m', AttributeUnits = 'knots', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_winddir_linear_10m', fstnomvar = 'WD', AttributeName = 'Wind_direction_at_10m', AttributeUnits = 'degrees', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_u-component_linear_10m', fstnomvar = 'UU', AttributeName = 'Wind_speed_U-component_at_10m', AttributeUnits = '\"m s**-1\"', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.5144444444444444444))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_v-component_linear_10m', fstnomvar = 'VV', AttributeName = 'Wind_spped_V-component_at_10m', AttributeUnits = '\"m s**-1\"', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.5144444444444444444))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_rain_linear', fstnomvar = 'PR', AttributeName = 'Total_precipitation_rate_at_surface', AttributeUnits = '\"kg m**-2 s**-1\"', intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.27777777777777777778*(60.0/FST_RECORD_MINUTES)))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_rain_acc_linear_mm', fstnomvar = 'PR', AttributeName = 'Total_precipitation_accumulated_at_surface', AttributeUnits = 'mm', intpopt = rmn.EZ_INTERP_LINEAR, constmul = 1000.0))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_rain_acc_linear_m', fstnomvar = 'PR', AttributeName = 'Total_precipitation_accumulated_at_surface', AttributeUnits = 'm', intpopt = rmn.EZ_INTERP_LINEAR))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_temperature_nearest_40m_K', fstnomvar = 'TT', AttributeName = 'Air_temperature_at_40m', AttributeUnits = 'K', fstip1 = 11950, intpopt = rmn.EZ_INTERP_NEAREST, constadd = 273.16))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_temperature_nearest_40m_dC', fstnomvar = 'TT', AttributeName = 'Air_temperature_at_40m', AttributeUnits = '\"degrees C\"', fstip1 = 11950, intpopt = rmn.EZ_INTERP_NEAREST))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_temperature_nearest_2m_K', fstnomvar = 'TT', AttributeName = 'Air_temperature_at_2m', AttributeUnits = 'K', fstip1 = 12000, intpopt = rmn.EZ_INTERP_NEAREST, constadd = 273.16))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_temperature_nearest_2m_dC', fstnomvar = 'TT', AttributeName = 'Air_temperature_at_2m', AttributeUnits = '\"degrees C\"', fstip1 = 12000, intpopt = rmn.EZ_INTERP_NEAREST))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_specific_humidity_nearest_40m', fstnomvar = 'HU', AttributeName = 'Specific_humidity_40m', AttributeUnits = '\"kg kg**-1\"', fstip1 = 11950, intpopt = rmn.EZ_INTERP_NEAREST))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_specific_humidity_nearest_2m', fstnomvar = 'HU', AttributeName = 'Specific_humidity_2m', AttributeUnits = '\"kg kg**-1\"', fstip1 = 12000, intpopt = rmn.EZ_INTERP_NEAREST))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_pres_nearest', fstnomvar = 'P0', AttributeName = 'Air_pressure_at_surface', AttributeUnits = 'Pa', intpopt = rmn.EZ_INTERP_NEAREST, constmul = 100.0))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_longwave_incoming_nearest', fstnomvar = 'FI', AttributeName = 'Incoming_longwave_down_incident_at_surface', AttributeUnits = '\"W m**-2\"', intpopt = rmn.EZ_INTERP_NEAREST))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_shortwave_incoming_nearest', fstnomvar = 'FB', AttributeName = 'Incoming_shortwave_down_incident_at_surface', AttributeUnits = '\"W m**-2\"', intpopt = rmn.EZ_INTERP_NEAREST))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_nearest_40m', fstnomvar = 'UV', AttributeName = 'Wind_speed_at_40m', AttributeUnits = '\"m s**-1\"', fstip1 = 11950, intpopt = rmn.EZ_INTERP_NEAREST, constmul = 0.5144444444444444444))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_nearest_40m_knots', fstnomvar = 'UV', AttributeName = 'Wind_speed_at_40m', AttributeUnits = 'knots', fstip1 = 11950, intpopt = rmn.EZ_INTERP_NEAREST))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_winddir_nearest_40m', fstnomvar = 'WD', AttributeName = 'Wind_direction_at_40m', AttributeUnits = 'degrees', fstip1 = 11950, intpopt = rmn.EZ_INTERP_NEAREST))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_u-component_nearest_40m', fstnomvar = 'UU', AttributeName = 'Wind_speed_U-component_at_40m', AttributeUnits = '\"m s**-1\"', fstip1 = 11950, intpopt = rmn.EZ_INTERP_NEAREST, constmul = 0.5144444444444444444))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_v-component_nearest_40m', fstnomvar = 'VV', AttributeName = 'Wind_spped_V-component_at_40m', AttributeUnits = '\"m s**-1\"', fstip1 = 11950, intpopt = rmn.EZ_INTERP_NEAREST, constmul = 0.5144444444444444444))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_nearest_10m', fstnomvar = 'UV', AttributeName = 'Wind_speed_at_10m', AttributeUnits = '\"m s**-1\"', fstip1 = 12000, intpopt = rmn.EZ_INTERP_NEAREST, constmul = 0.5144444444444444444))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_nearest_10m_knots', fstnomvar = 'UV', AttributeName = 'Wind_speed_at_10m', AttributeUnits = 'knots', fstip1 = 12000, intpopt = rmn.EZ_INTERP_NEAREST))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_winddir_nearest_10m', fstnomvar = 'WD', AttributeName = 'Wind_direction_at_10m', AttributeUnits = 'degrees', fstip1 = 12000, intpopt = rmn.EZ_INTERP_NEAREST))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_u-component_nearest_10m', fstnomvar = 'UU', AttributeName = 'Wind_speed_U-component_at_10m', AttributeUnits = '\"m s**-1\"', fstip1 = 12000, intpopt = rmn.EZ_INTERP_NEAREST, constmul = 0.5144444444444444444))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_wind_v-component_nearest_10m', fstnomvar = 'VV', AttributeName = 'Wind_spped_V-component_at_10m', AttributeUnits = '\"m s**-1\"', fstip1 = 12000, intpopt = rmn.EZ_INTERP_NEAREST, constmul = 0.5144444444444444444))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_rain_nearest', fstnomvar = 'PR', AttributeName = 'Total_precipitation_rate_at_surface', AttributeUnits = '\"kg m**-2 s**-1\"', intpopt = rmn.EZ_INTERP_NEAREST, constmul = 0.27777777777777777778*(60.0/FST_RECORD_MINUTES)))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_rain_acc_nearest_mm', fstnomvar = 'PR', AttributeName = 'Total_precipitation_accumulated_at_surface', AttributeUnits = 'mm', intpopt = rmn.EZ_INTERP_NEAREST, constmul = 1000.0))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'gdps_rain_acc_nearest_m', fstnomvar = 'PR', AttributeName = 'Total_precipitation_accumulated_at_surface', AttributeUnits = 'm', intpopt = rmn.EZ_INTERP_NEAREST))

# Outputs files.

for i, c in enumerate(PROCESS_FSTCONVFLD):
	with open(c.fname + '.meta', 'wb') as t:
		if (not c.AttributeName is None):
			t.write('%s %s\n' % ('AttributeName:', c.AttributeName))
		if (not c.AttributeType is None):
			t.write('%s %s\n' % ('AttributeType:', c.AttributeType))
		if (not c.AttributeUnits is None):
			t.write('%s %s\n' % ('AttributeUnits:', c.AttributeUnits))
                t.write('Field = min(max(%g*Source + %g), %g), %g)\n' % (c.constmul, c.constadd, c.constrmin, c.constrmax))
		t.close()
	c.fid = csv.writer(open(c.fname + '.csv', 'wb'))
	c.fid.writerow(np.concatenate((['Station'], na)))
	c.fid.writerow(np.concatenate((['Latitude'], la)))
	c.fid.writerow(np.concatenate((['Longitude'], lo)))

# Iterate time loop.

while FST_CURRENT_TIME < FST_STOP_BEFORE_TIME:

        # Add DST offset to print only standard time to file (to avoid irregular time-stamps).

        FRIENDLY_TIME = FST_CURRENT_TIME.replace(tzinfo = None) + UTC_STD_OFFSET

	# Open file.

	fstsrc = utctimetofstfname_gdps(FST_CURRENT_TIME)
	fstfid = rmn.fstopenall(fstsrc['path'])
	print('%s %s' % (strftime('%Y/%m/%d %H:%M:%S', FRIENDLY_TIME.timetuple()), fstsrc['path']))

	# Records.

	for i, c in enumerate(PROCESS_FSTCONVFLD):
		rec = latlonvalfromfst(la, lo, fstfid, fstnomvar = c.fstnomvar, fstetiket = c.fstetiket, fstip1 = c.fstip1, fstip2 = fstsrc['ip2'], intpopt = c.intpopt, constmul = c.constmul, constadd = c.constadd, constrmax = c.constrmax, constrmin = c.constrmin)
		c.fid.writerow(np.concatenate(([str(FRIENDLY_TIME)], rec)))

	# Close the file.

	rmn.fstcloseall(fstfid)

	# Increment time.

	FST_CURRENT_TIME += dt.relativedelta(minutes = FST_RECORD_MINUTES)
