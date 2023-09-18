#!/usr/bin/python

from os import path
from time import gmtime, strftime
from datetime import datetime
from dateutil import relativedelta as dt, tz, parser as dtparser
import numpy as np
import rpnpy.librmn.all as rmn
from ensim_utils import *

# OPTIONAL
# pip2 install --user 'timezonefinder<3.2.1'
# Version 3.2.1 seems to have an error.

###from timezonefinder import TimezoneFinder

# To load rpnpy:
# . s.ssmuse.dot ENV/py/2.7/rpnpy/2.0.4

# Archive paths.

PATH_ARMNMSH = '/fs/site2/dev/eccc/mrd/rpnenv/smsh001'
PATH_RARC_MISSING = '/fs/site2/dev/eccc/cmd/n/dap000/sa_mesh_forcing/rarc'

def utctimetofstfname_rdrs(utctime):

	# 00:00->23:00

	filetime = utctime
	filefcst = 12
	fstsrcpath = PATH_ARMNMSH + ('/%04d%02d%02d%02d_forcing' % (filetime.year, filetime.month, filetime.day, filefcst))

	# Return file path and adjust ip2.
	# 01:00->24:00

	return { 'path': fstsrcpath, 'ip2': (filetime.hour + 1) }

def utctimetofstfname_rdps(utctime, ip2 = None):

	# 00:00->05:00 ; 12-hour forecast of yesterday.

	if (utctime.hour < 6):
		filetime = utctime + dt.relativedelta(hours = -12)
		filefcst = 12

	# 06:00->17:00 ; 00-hour forecast of today.

	elif (utctime.hour < 18):
		filetime = utctime
		filefcst = 0

	# 18:00->23:00 ; 12-hour forecast of today.

	else:
		filetime = utctime + dt.relativedelta(hours = -12)
		filefcst = 12

	# ip2 override.

	if (not ip2 is None):
		filetime = filetime.replace(hour = ip2)

	# Special rules.

	if (utctime < dtparser.parse('Sep 30, 2011 00:00:00 +0000')):
		fstsrcpath = PATH_ARMNMSH + ('/forcage/regeta_op_0618/%04d%02d%02d%02d' % (filetime.year, filetime.month, filetime.day, filefcst))
	else:
		fstsrcpath = PATH_ARMNMSH + ('/arcsfc/%04d/%02d/%02d/regeta/%04d%02d%02d%02d_%03d' % (filetime.year, filetime.month, filetime.day, filetime.year, filetime.month, filetime.day, filefcst, filetime.hour))

	# Check rarc backup if file does not exist.

	if (not path.exists(fstsrcpath)):
		fstsrcpath = PATH_RARC_MISSING + ('/operation.forecasts.regeta/%04d%02d%02d%02d_%03d' % (filetime.year, filetime.month, filetime.day, filefcst, filetime.hour))

	# Stop if the path does not exist.

	if (not path.exists(fstsrcpath)):
		print('ERROR: Path does not exist. Script cannot continue. ' + fstsrcpath)
		exit()

	# Return file path and adjust ip2.

	return { 'path': fstsrcpath, 'ip2': filetime.hour }

def utctimetofstfname_gem(utctime, ip2 = None):

	# RDPS.

	return utctimetofstfname_rdps(utctime, ip2)

def utctimetofstfname_gdps(utctime, ip2 = None):

	# 00:00->05:00 ; 12-hour forecast of yesterday.

	if (utctime.hour < 6):
		filetime = utctime + dt.relativedelta(hours = -12)
		filefcst = 12

	# 06:00->17:00 ; 00-hour forecast of today.

	elif (utctime.hour < 18):
		filetime = utctime
		filefcst = 0

	# 18:00->23:00 ; 12-hour forecast of today.

	else:
		filetime = utctime + dt.relativedelta(hours = -12)
		filefcst = 12

	# ip2 override.

	if (not ip2 is None):
		filetime = filetime.replace(hour = ip2)

	# Special rules.

	fstsrcpath = PATH_ARMNMSH + ('/arcsfc/%04d/%02d/%02d/glbeta/%04d%02d%02d%02d_%03d' % (filetime.year, filetime.month, filetime.day, filetime.year, filetime.month, filetime.day, filefcst, filetime.hour))

	# Check rarc backup if file does not exist.

	if (not path.exists(fstsrcpath)):
		print('WARNING: Path does not exist, switching to local archive from: %s' % fstsrcpath)
		fstsrcpath = PATH_RARC_MISSING + ('/operation.forecasts.glbeta/%04d%02d%02d%02d_%03d' % (filetime.year, filetime.month, filetime.day, filefcst, filetime.hour))

	# Stop if the path does not exist.

	if (not path.exists(fstsrcpath)):
		print('ERROR: Path does not exist. Script cannot continue. ' + fstsrcpath)
		exit()

	# Return file path and adjust ip2.

	return { 'path': fstsrcpath, 'ip2': filetime.hour }

def utctimetofstfname_hrdps(utctime, ip2 = None):

	# 00:00->05:00 ; 12-hour forecast of yesterday.

	if (utctime.hour < 6):
		filetime = utctime + dt.relativedelta(hours = -12)
		filefcst = 12

	# 06:00->17:00 ; 00-hour forecast of today.

	elif (utctime.hour < 18):
		filetime = utctime
		filefcst = 0

	# 18:00->23:00 ; 12-hour forecast of today.

	else:
		filetime = utctime + dt.relativedelta(hours = -12)
		filefcst = 12

	# ip2 override.

	if (not ip2 is None):
		filetime = filetime.replace(hour = ip2)

	# Default filename.

	fstfname = '%04d%02d%02d%02d_%03d' % (filetime.year, filetime.month, filetime.day, filefcst, filetime.hour)

	# Special rules.

	if (utctime < dtparser.parse('Dec 15, 2015 18:00:00 +0000')):
		fstfname = fstfname + '_2.5km'

	# Default path.

	fstsrcpath = PATH_ARMNMSH + ('/arcsfc/%04d/%02d/%02d/lam.nat.eta/' % (filetime.year, filetime.month, filetime.day)) + fstfname

	# Check rarc backup if file does not exist.

	if (not path.exists(fstsrcpath)):
		print('WARNING: Path does not exist, switching to local archive from: %s' % fstsrcpath)
		fstsrcpath = PATH_RARC_MISSING + '/operation.forecasts.lam.nat.eta/' + fstfname

	# Stop if the path does not exist.

	if (not path.exists(fstsrcpath)):
		print('ERROR: Path does not exist. Script cannot continue. ' + fstsrcpath)
		exit()

	# Return file path and adjust ip2.

	return { 'path': fstsrcpath, 'ip2': filetime.hour }

def utctimetofstfname_capa(utctime):

	# 00:00 -> 06:00 ; 06-h.

	if (utctime.hour < 6):
		filetime = utctime + dt.relativedelta(hour = 6)
		filefcst = 6

	# 06:00 -> 12:00 ; 12-h.

	elif (utctime.hour < 12):
		filetime = utctime + dt.relativedelta(hour = 12)
		filefcst = 12

	# 12:00 -> 18:00 ; 18-h.

	elif (utctime.hour < 18):
		filetime = utctime + dt.relativedelta(hour = 18)
		filefcst = 18

	# 18:00 -> 00:00 + 1 day ; 00-h + 1-day.

	else:
		filetime = utctime + dt.relativedelta(days = +1, hour = 0)
		filefcst = 0

	# Special rules.

	if (utctime < dtparser.parse('Jun 30, 2012 00:00:00 +0000')):
		fstsrcpath = PATH_ARMNMSH + '/capa/v2.4b8-reanalyse/6h/final/' + ('%04d/' % filetime.year) + ('%02d/' % filetime.month) + ('%04d' % filetime.year) + ('%02d' % filetime.month) + ('%02d' % filetime.day) + ('%02d_000' % filefcst)
	elif (utctime < dtparser.parse('Dec 1, 2021 00:00:00 +0000')):
		fstsrcpath = PATH_ARMNMSH + '/capa/v2.3/analyse/6h/final/' + ('%04d' % filetime.year) + ('%02d' % filetime.month) + ('%02d' % filetime.day) + ('%02d_000' % filefcst)
	else:
		fstsrcpath = PATH_ARMNMSH + '/capa/rdpa/final/analyse/6h/' + ('%04d' % filetime.year) + ('%02d' % filetime.month) + ('%02d' % filetime.day) + ('%02d_000' % filefcst)

	# Check rarc backup if file does not exist.

	if (not path.exists(fstsrcpath)):
		fstsrcpath = PATH_RARC_MISSING + '/operation.analyses.regcapa.6h.final/' + ('%04d' % filetime.year) + ('%02d' % filetime.month) + ('%02d' % filetime.day) + ('%02d_000' % filefcst)

	# Stop if the path does not exist.

	if (not path.exists(fstsrcpath)):
		print('ERROR: Path does not exist. Script cannot continue. ' + fstsrcpath)
		exit()

	# Return file path and adjust ip2.

	return { 'path' : fstsrcpath, 'ip2' : filetime.hour }

def r2ctimeseriesfromfst(
	R2CSHED_INFILE = 'MESH_drainage_database.r2c',
	PROCESS_FSTCONVFLD = [],
	START_TIME = datetime(2004, 10, 1, tzinfo = tz.tzutc()),
	STOP_BEFORE_TIME = datetime(2012, 10, 1, tzinfo = tz.tzutc()),
	I_COUNTER = 1,
	LOCAL_TIME_ZONE = tz.tzutc()
	):

	# Stop if input file is not defined.

	print('REMARK: Reading %s' % R2CSHED_INFILE)
	if (R2CSHED_INFILE == '' or (not path.exists(R2CSHED_INFILE))):
		print('ERROR: Shed file is not defined or does not exist. The script cannot continue.')
		exit()

	# Read the header from the r2c input file.

	r2c = r2cfile()
	r2cgridfromr2c(r2c, R2CSHED_INFILE)
	fstmatchgrid = fstgridfromr2c(r2c)

	# OPTIONAL.
	# pip2 install --user 'timezonefinder<3.2.1'
	# Version 3.2.1 seems to have an error.
	# Derive timezone from centre location in grid.
	# Add DST offset to print only standard time to file (to avoid irregular time-stamps).

###	if (START_TIME.tzinfo is None):
###		if (r2c.grid.Projection.lower() == 'latlong'):
###			clon = r2c.grid.xOrigin + (r2c.grid.xCount + 1)*r2c.grid.xDelta/2.0
###			clat = r2c.grid.yOrigin + (r2c.grid.yCount + 1)*r2c.grid.yDelta/2.0
###			ctz = TimezoneFinder().timezone_at(lng = clon, lat = clat)
###			LOCAL_TIME_ZONE = tz.gettz(ctz)
###		START_TIME = START_TIME.replace(tzinfo = LOCAL_TIME_ZONE)
###		STOP_BEFORE_TIME = STOP_BEFORE_TIME.replace(tzinfo = LOCAL_TIME_ZONE)

	# Initialize time loop.
	# 60 minute stepping for GEM (RDPS).

	UTC_STD_OFFSET = LOCAL_TIME_ZONE.utcoffset(START_TIME) - LOCAL_TIME_ZONE.dst(START_TIME)
	FST_START_TIME = START_TIME.astimezone(tz.tzutc()) + LOCAL_TIME_ZONE.dst(START_TIME)
	FST_STOP_BEFORE_TIME = STOP_BEFORE_TIME.astimezone(tz.tzutc()) + LOCAL_TIME_ZONE.dst(STOP_BEFORE_TIME)
	FST_RECORD_MINUTES = +60
	FST_CURRENT_TIME = FST_START_TIME

	# Default parameters.

	if (not PROCESS_FSTCONVFLD):
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_temperature_40m.r2c', fstnomvar = 'TT', AttributeName = 'Air_temperature_at_40m', AttributeUnits = 'K', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR, constadd = 273.16))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_temperature_2m.r2c', fstnomvar = 'TT', AttributeName = 'Air_temperature_at_2m', AttributeUnits = 'K', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR, constadd = 273.16))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_humidity_40m.r2c', fstnomvar = 'HU', AttributeName = 'Specific_humidity_40m', AttributeUnits = 'kg kg**-1', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_humidity_2m.r2c', fstnomvar = 'HU', AttributeName = 'Specific_humidity_2m', AttributeUnits = 'kg kg**-1', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_pres.r2c', fstnomvar = 'P0', AttributeName = 'Air_pressure_at_surface', AttributeUnits = 'Pa', intpopt = rmn.EZ_INTERP_LINEAR, constmul = 100.0))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_longwave.r2c', fstnomvar = 'FI', AttributeName = 'Incoming_longwave_at_surface', AttributeUnits = 'W m**-2', intpopt = rmn.EZ_INTERP_LINEAR))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_shortwave.r2c', fstnomvar = 'FB', AttributeName = 'Incoming_shortwave_at_surface', AttributeUnits = 'W m**-2', intpopt = rmn.EZ_INTERP_LINEAR))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_wind_40m.r2c', fstnomvar = 'UV', AttributeName = 'Wind_speed_at_40m', AttributeUnits = 'm s**-1', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.5144444444444444444))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_winddir_40m.r2c', fstnomvar = 'WD', AttributeName = 'Wind_direction_at_40m', AttributeUnits = 'degrees', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_wind_u-component_40m.r2c', fstnomvar = 'UU', AttributeName = 'Wind_speed_U-component_at_40m', AttributeUnits = 'm s**-1', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.5144444444444444444))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_wind_v-component_40m.r2c', fstnomvar = 'VV', AttributeName = 'Wind_spped_V-component_at_40m', AttributeUnits = 'm s**-1', fstip1 = 11950, intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.5144444444444444444))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_wind_10m.r2c', fstnomvar = 'UV', AttributeName = 'Wind_speed_at_10m', AttributeUnits = 'm s**-1', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.5144444444444444444))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_winddir_10m.r2c', fstnomvar = 'WD', AttributeName = 'Wind_direction_at_10m', AttributeUnits = 'degrees', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_wind_u-component_10m.r2c', fstnomvar = 'UU', AttributeName = 'Wind_speed_U-component_at_10m', AttributeUnits = 'm s**-1', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.5144444444444444444))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_wind_v-component_10m.r2c', fstnomvar = 'VV', AttributeName = 'Wind_spped_V-component_at_10m', AttributeUnits = 'm s**-1', fstip1 = 12000, intpopt = rmn.EZ_INTERP_LINEAR, constmul = 0.5144444444444444444))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_precip_acc.r2c', fstnomvar = 'PR_deacc', AttributeName = 'Total_precipitation_accumulated_at_surface', AttributeUnits = 'kg m**-2', constmul = 1000.0))
		PROCESS_FSTCONVFLD.append(r2cconversionfieldfromfst(fpathr2cout = 'basin_precip_rate.r2c', fstnomvar = 'PR_deacc', AttributeName = 'Total_precipitation_rate_at_surface', AttributeUnits = '\"kg m**-2 s**-1\"', constmul = 0.27777777777777777778*(60.0/FST_RECORD_MINUTES)))

	# Read header from r2c input file and create r2c output files.

	for i, c in enumerate(PROCESS_FSTCONVFLD):
		r2cgridfromr2c(c.r2c, R2CSHED_INFILE)
		r2cfilecreateheader(c.r2c, c.fpathr2cout)

	# Iterate time loop.

	fstopenpath = None
	fstfid = None
	p0openpath = None
	p0fid = None
	while FST_CURRENT_TIME < FST_STOP_BEFORE_TIME:

		# Open file.

#		fstsrc = utctimetofstfname_rdps(FST_CURRENT_TIME)
#		fstsrc = utctimetofstfname_gem(FST_CURRENT_TIME)
#		fstsrc = utctimetofstfname_capa(FST_CURRENT_TIME)
#		fstfid = rmn.fstopenall(fstsrc['path'])

		# Records.
		# Add DST offset to print only standard time to file (to avoid irregular time-stamps).

		FRIENDLY_TIME = FST_CURRENT_TIME.replace(tzinfo = None) + UTC_STD_OFFSET
#		print('%s %s %s %03d' % (strftime('%Y/%m/%d %H:%M:%S', FRIENDLY_TIME.timetuple()), fstsrc['path'], 'ip2', fstsrc['ip2']))
		print('INFO: Processing for datetime \'%s\'' % strftime('%Y/%m/%d %H:%M:%S', FRIENDLY_TIME.timetuple()))
		for i, c in enumerate(PROCESS_FSTCONVFLD):
			if (c.fpathsystem in ['rdps', 'gem']):
				fstsrc = utctimetofstfname_rdps(FST_CURRENT_TIME)
			elif (c.fpathsystem in ['gdps']):
				fstsrc = utctimetofstfname_gdps(FST_CURRENT_TIME)
			elif (c.fpathsystem in ['hrdps']):
				fstsrc = utctimetofstfname_hrdps(FST_CURRENT_TIME)
			elif (c.fpathsystem in ['rdpa', 'capa']):
				fstsrc = utctimetofstfname_capa(FST_CURRENT_TIME)
			elif (c.fpathsystem == 'rdrs'):
				fstsrc = utctimetofstfname_rdps(FST_CURRENT_TIME)
			else:
				print('ERROR: Unknown system path \'%s\'.' % c.fpathsystem)
				exit()
			if (fstsrc['path'] != fstopenpath):
				if (fstfid is not None):
					rmn.fstcloseall(fstfid)
				fstopenpath = fstsrc['path']
				fstfid = rmn.fstopenall(fstsrc['path'])
#			print('INFO: Processing \'%s\' for \'%s\' from %s with ip2 = %03d' % (c.fstnomvar, c.r2c.attr[0].AttributeName, fstsrc['path'], fstsrc['ip2']))
			r2cattributefromfst(c.r2c.attr[0], fstmatchgrid, fstfid, fstnomvar = c.fstnomvar.upper().replace('_DEACC', ''), fstetiket = c.fstetiket, fstip1 = c.fstip1, fstip2 = fstsrc['ip2'], intpopt = c.intpopt, constmul = c.constmul, constadd = c.constadd, constrmax = c.constrmax, constrmin = c.constrmin)
			if ('_DEACC' in c.fstnomvar.upper()):
#				p0src = utctimetofstfname_gem(FST_CURRENT_TIME, fstsrc['ip2'] - int(FST_RECORD_MINUTES/60))
				if (c.fpathsystem in ['rdps', 'gem']):
					p0src = utctimetofstfname_rdps(FST_CURRENT_TIME, fstsrc['ip2'] - int(FST_RECORD_MINUTES/60))
				elif (c.fpathsystem in ['gdps']):
					p0src = utctimetofstfname_gdps(FST_CURRENT_TIME, fstsrc['ip2'] - int(FST_RECORD_MINUTES/60))
				elif (c.fpathsystem in ['hrdps']):
					p0src = utctimetofstfname_hrdps(FST_CURRENT_TIME, fstsrc['ip2'] - int(FST_RECORD_MINUTES/60))
				elif (c.fpathsystem in ['rdpa', 'capa']):
					p0src = utctimetofstfname_capa(FST_CURRENT_TIME, fstsrc['ip2'] - int(FST_RECORD_MINUTES/60))
				elif (c.fpathsystem == 'rdrs'):
					p0src = utctimetofstfname_rdps(FST_CURRENT_TIME, fstsrc['ip2'] - int(FST_RECORD_MINUTES/60))
				if (p0src['path'] != p0openpath):
					if (p0fid is not None):
						rmn.fstcloseall(p0fid)
					p0openpath = p0src['path']
					p0fid = rmn.fstopenall(p0src['path'])
				p1 = c.r2c.attr[0].AttributeData
				r2cattributefromfst(c.r2c.attr[0], fstmatchgrid, p0fid, fstnomvar = c.fstnomvar.upper().replace('_DEACC', ''), fstetiket = c.fstetiket, fstip1 = c.fstip1, fstip2 = p0src['ip2'], intpopt = c.intpopt, constmul = c.constmul, constadd = c.constadd, constrmax = c.constrmax, constrmin = c.constrmin)
#				rmn.fstcloseall(p0fid)
				c.r2c.attr[0].AttributeData = p1 - c.r2c.attr[0].AttributeData
			r2cfileappendmultiframe(c.r2c, c.fpathr2cout, I_COUNTER, FRIENDLY_TIME)
#			rmn.fstcloseall(fstfid)

		# Increment time and frame counter.

		FST_CURRENT_TIME += dt.relativedelta(minutes = FST_RECORD_MINUTES)
		I_COUNTER += 1

	# Close file.

	if (fstfid is not None):
		rmn.fstcloseall(fstfid)
		if (p0fid is not None):
			rmn.fstcloseall(p0fid)
	print('INFO: Processing has completed at frame %d.' % (I_COUNTER - 1))

	# Return counter.
	return I_COUNTER
