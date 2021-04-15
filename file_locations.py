#!/usr/bin/python
from os import path
from dateutil import relativedelta as dt, parser as dtparser

# Archive paths.
PATH_ARMNMSH = '/home/smsh001/data/eccc-ppp4'
PATH_RDRSv2 = '/home/smco813/ss4/CaSPAR_set_no1'
PATH_RARC_MISSING = ''

def utctimetofstfname_rdrs_v2(utctime):

	# 00:00->23:00
	filetime = utctime
	filefcst = 12
	fstsrcpath = PATH_RDRSv2 + ('/%04d/%02d/%04d%02d%02d%02d_forcings' % (filetime.year, filetime.month, filetime.year, filetime.month, filetime.day, filefcst))

	# Stop if the path does not exist.
	if (not path.exists(fstsrcpath)):
		print('ERROR: Path does not exist. Script cannot continue. ' + fstsrcpath)
		exit()

	# Return file path and adjust ip2.
	# 01:00->24:00
	return { 'path': fstsrcpath, 'ip2': (filetime.hour + 1) }

def utctimetofstfname_rdps(utctime):

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

def utctimetofstfname_rdpa(utctime):

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
	else:
		fstsrcpath = PATH_ARMNMSH + '/capa/v2.3/analyse/6h/final/' + ('%04d' % filetime.year) + ('%02d' % filetime.month) + ('%02d' % filetime.day) + ('%02d_000' % filefcst)

	# Check rarc backup if file does not exist.
	if (not path.exists(fstsrcpath)):
		fstsrcpath = PATH_RARC_MISSING + '/operation.analyses.regcapa.6h.final/' + ('%04d' % filetime.year) + ('%02d' % filetime.month) + ('%02d' % filetime.day) + ('%02d_000' % filefcst)

	# Stop if the path does not exist.
	if (not path.exists(fstsrcpath)):
		print('ERROR: Path does not exist. Script cannot continue. ' + fstsrcpath)
		exit()

	# Return file path and adjust ip2.
	return { 'path' : fstsrcpath, 'ip2' : filetime.hour }
