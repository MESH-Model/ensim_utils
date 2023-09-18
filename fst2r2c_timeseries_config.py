#!/usr/bin/python
from fst2r2c_timeseries import *
from dateutil import tz

# To load rpnpy:
# . s.ssmuse.dot ENV/py/2.7/rpnpy/2.0.4

# Start/stop times.
START_TIME = datetime(year = 2023, month = 1, day = 1, hour = 0, tzinfo = tz.gettz('EST'))
STOP_BEFORE_TIME = datetime(year = 2023, month = 2, day = 1, hour = 0, tzinfo = tz.gettz('EST'))
DATE_MARK = '_%s_%s' % (strftime('%Y%m%d', START_TIME.timetuple()), strftime('%Y%m%d', STOP_BEFORE_TIME.timetuple()))

# Fields.
PROCESS_FSTCONVFLD = []
#GEM
PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = ('basin_temperature_nearest_next%s.r2c' % DATE_MARK), fstnomvar = 'TT', AttributeName = 'Air_temperature_at_40m', AttributeUnits = 'K', fpathsystem = 'rdps', constadd = 273.16))
PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = ('basin_humidity_nearest_next%s.r2c' % DATE_MARK), fstnomvar = 'HU', AttributeName = 'Specific_humidity_40m', AttributeUnits = 'kg kg**-1', fpathsystem = 'rdps'))
PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = ('basin_pres_nearest_next%s.r2c' % DATE_MARK), fstnomvar = 'P0', AttributeName = 'Air_pressure_at_surface', AttributeUnits = 'Pa', fpathsystem = 'rdps', constmul = 100.0))
PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = ('basin_longwave_linear_next%s.r2c' % DATE_MARK), fstnomvar = 'FI', AttributeName = 'Incoming_longwave_down_incident_at_surface', AttributeUnits = 'W m**-2', fpathsystem = 'rdps', intpopt = rmn.EZ_INTERP_LINEAR, constrmin = 0.0))
PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = ('basin_shortwave_linear_next%s.r2c' % DATE_MARK), fstnomvar = 'FB', AttributeName = 'Incoming_shortwave_down_incident_at_surface', AttributeUnits = 'W m**-2', fpathsystem = 'rdps', intpopt = rmn.EZ_INTERP_LINEAR, constrmin = 0.0))
PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = ('basin_wind_nearest_next%s.r2c' % DATE_MARK), fstnomvar = 'UV', AttributeName = 'Wind_speed_at_40m', AttributeUnits = 'm s**-1', fpathsystem = 'rdps', constmul = 0.5144444444444444444))
#PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = ('basin_rain_linear_next%s.r2c' % DATE_MARK), fstnomvar = 'PR0', AttributeName = 'Total_precipitation_rate_at_surface', AttributeUnits = 'kg m**-2 s**-1', fpathsystem = 'rdps', intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.2777777777777778, constrmin = 0.0))
#CaPA
PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = ('basin_rain_linear_next%s.r2c' % DATE_MARK), fstnomvar = 'PR', AttributeName = 'Total_precipitation_rate_at_surface', AttributeUnits = 'kg m**-2 s**-1', fpathsystem = 'rdpa', intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.2777777777777778, constrmin = 0.0))

# Process files.
r2ctimeseriesfromfst(
  PROCESS_FSTCONVFLD = PROCESS_FSTCONVFLD,
  START_TIME = START_TIME,
  STOP_BEFORE_TIME = STOP_BEFORE_TIME
)
