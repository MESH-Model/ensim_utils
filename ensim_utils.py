#!/usr/bin/python

from os import path
from time import gmtime, strftime, mktime
import numpy as np
import rpnpy.librmn.all as rmn

# To load rpnpy:
# . s.ssmuse.dot ENV/py/2.7/rpnpy/2.0.4

# r2c structures.

class r2cmeta(object):
	def __init__(self):
		self.SourceFileName = ''
		self.NominalGridSize_AL = 1.0
		self.ContourInterval = 1.0
		self.ImperviousArea = 0.0
		self.ClassCount = 0
		self.NumRiverClasses = 0
		self.ElevConversion = 1.0
		self.TotalNumOfGrids = 0
		self.NumGridsInBasin = 0
		self.DebugGridNo = 0

class r2cgrid(object):
	def __init__(self):
		self.Projection = 'UNKNOWN'
		self.Ellipsoid = 'UNKNOWN'
		self.xOrigin = 0.0
		self.yOrigin = 0.0
		self.xCount = 0
		self.yCount = 0
		self.xDelta = 0.0
		self.yDelta = 0.0

class r2cattribute(object):
	def __init__(self, AttributeName = None, AttributeType = None, AttributeUnits = None, AttributeData = None):
		self.AttributeName = AttributeName
		self.AttributeType = AttributeType
		self.AttributeUnits = AttributeUnits
		self.AttributeData = AttributeData
		self.FrameCount = 0

class r2cfile(object):
	def __init__(self):
		self.meta = None
		self.grid = r2cgrid()
		self.attr = []

class r2cconversionfieldfromfst(object):
        def __init__(self, fpathr2cout, fstnomvar, AttributeName, AttributeType = None, AttributeUnits = None, fstetiket = ' ', fstip1 = -1, intpopt = rmn.EZ_INTERP_NEAREST, constmul = 1.0, constadd = 0.0, constrmax = float('inf'), constrmin = float('-inf')):
                self.r2c = r2cfile()
		self.r2c.attr.append(r2cattribute(AttributeName = AttributeName, AttributeType = AttributeType, AttributeUnits = AttributeUnits))
                self.fpathr2cout = fpathr2cout
                self.fstnomvar = fstnomvar
                self.fstetiket = fstetiket
                self.fstip1 = fstip1
                self.intpopt = intpopt
                self.constmul = constmul
                self.constadd = constadd
                self.constrmax = constrmax
                self.constrmin = constrmin

class conversionfieldfromfst(object):
        def __init__(self, fname, fstnomvar, AttributeName, AttributeType = None, AttributeUnits = None, fstetiket = ' ', fstip1 = -1, intpopt = rmn.EZ_INTERP_NEAREST, constmul = 1.0, constadd = 0.0, constrmax = float('inf'), constrmin = float('-inf')):
                self.fid = None
                self.fname = fname
		self.AttributeName = AttributeName
		self.AttributeType = AttributeType
		self.AttributeUnits = AttributeUnits
                self.fstnomvar = fstnomvar
                self.fstetiket = fstetiket
                self.fstip1 = fstip1
                self.intpopt = intpopt
                self.constmul = constmul
                self.constadd = constadd
                self.constrmax = constrmax
                self.constrmin = constrmin

# r2c routines.

def r2cfilecreateheader(r2c, fpathr2cout):

	# Write the header.
	# Writing the header overwrites any existing file.

	with open(fpathr2cout, 'w') as r2cfid:
		r2cfid.write('########################################\n')
		r2cfid.write(':FileType r2c ASCII EnSim 1.0\n')
		r2cfid.write('#\n')
		r2cfid.write('# DataType 2D Rect Cell\n')
		r2cfid.write('#\n')
		r2cfid.write(':Application ensim_utils.py\n')
		r2cfid.write(':Version 1.0\n')
		r2cfid.write(':WrittenBy ensim_utils.py\n')
		r2cfid.write(':CreationDate ' + strftime('%Y/%m/%d %H:%M:%S', gmtime()) + '\n')
		r2cfid.write('#\n')
		r2cfid.write('#---------------------------------------\n')
		r2cfid.write('#\n')
		if (not r2c.meta is None):
			r2cfid.write('#\n')
			r2cfid.write(':NominalGridSize_AL ' + str(r2c.meta.NominalGridSize_AL) + '\n')
			r2cfid.write(':ContourInterval ' + str(r2c.meta.ContourInterval) + '\n')
			r2cfid.write(':ImperviousArea ' + str(r2c.meta.ImperviousArea) + '\n')
			r2cfid.write(':ClassCount ' + str(r2c.meta.ClassCount) + '\n')
			r2cfid.write(':NumRiverClasses ' + str(r2c.meta.NumRiverClasses) + '\n')
			r2cfid.write(':ElevConversion ' + str(r2c.meta.ElevConversion) + '\n')
			r2cfid.write(':TotalNumOfGrids ' + str(r2c.meta.TotalNumOfGrids) + '\n')
			r2cfid.write(':NumGridsInBasin ' + str(r2c.meta.NumGridsInBasin) + '\n')
			r2cfid.write(':DebugGridNo ' + str(r2c.meta.DebugGridNo) + '\n')
		r2cfid.write('#\n')
		if (r2c.grid.Projection == 'LATLONG'):
			r2cfid.write(':Projection ' + r2c.grid.Projection + '\n')
			r2cfid.write(':Ellipsoid ' + r2c.grid.Ellipsoid + '\n')
		elif (r2c.grid.Projection == 'ROTLATLONG'):
			r2cfid.write(':Projection ' + r2c.grid.Projection + '\n')
			r2cfid.write(':CentreLatitude ' + str(r2c.grid.CentreLatitude) + '\n')
			r2cfid.write(':CentreLongitude ' + str(r2c.grid.CentreLongitude) + '\n')
			r2cfid.write(':RotationLatitude ' + str(r2c.grid.RotationLatitude) + '\n')
			r2cfid.write(':RotationLongitude ' + str(r2c.grid.RotationLongitude) + '\n')
			r2cfid.write(':Ellipsoid ' + r2c.grid.Ellipsoid + '\n')
		r2cfid.write('#\n')
		r2cfid.write(':xOrigin ' + str(r2c.grid.xOrigin) + '\n')
		r2cfid.write(':yOrigin ' + str(r2c.grid.yOrigin) + '\n')
		r2cfid.write('#\n')
		r2cfid.write('#\n')
		for i, a in enumerate(r2c.attr):
			if (not a.AttributeName is None):
				r2cfid.write(':AttributeName ' + str(i + 1) + ' ' + a.AttributeName + '\n')
			else:
				r2cfid.write(':AttributeName ' + str(i + 1) + ' Attribute' + str(i + 1) + '\n')
			if (not a.AttributeType is None):
				r2cfid.write(':AttributeType ' + str(i + 1) + ' ' + a.AttributeType + '\n')
			if (not a.AttributeUnits is None):
				r2cfid.write(':AttributeUnits ' + str(i + 1) + ' ' + a.AttributeUnits + '\n')
		r2cfid.write('#\n')
		r2cfid.write(':xCount ' + str(r2c.grid.xCount) + '\n')
		r2cfid.write(':yCount ' + str(r2c.grid.yCount) + '\n')
		r2cfid.write(':xDelta ' + str(r2c.grid.xDelta) + '\n')
		r2cfid.write(':yDelta ' + str(r2c.grid.yDelta) + '\n')
		r2cfid.write('#\n')
		r2cfid.write('#\n')
		r2cfid.write(':EndHeader\n')

def r2cfileappendattributes(r2c, fpathr2cout):

	# Data.
	# Will append to existing file.

	with open(fpathr2cout, 'a') as r2cfid:
		for i, a in enumerate(r2c.attr):
			if (not a.AttributeName is None):
				print('Saving ... ' + a.AttributeName)
			else:
				print('Saving ... Attribute ' + str(i + 1))
			np.savetxt(r2cfid, np.transpose(a.AttributeData), fmt = '%g')

def r2cfileappendmultiframe(r2c, fpathr2cout, frameno, frametime):

	# Data frame.
	# Will append to existing file.
	# Standard date format for r2c: "yyyy/MM/dd HH:mm:ss.SSS".

	r2c.attr[0].FrameCount += 1
	frameno = r2c.attr[0].FrameCount
	with open(fpathr2cout, 'a') as r2cfid:
		r2cfid.write(':Frame %d %d \"%s\"\n' % (frameno, frameno, strftime('%Y/%m/%d %H:%M:%S', frametime.timetuple())))
		np.savetxt(r2cfid, np.transpose(r2c.attr[0].AttributeData), fmt = '%g')
		r2cfid.write(':EndFrame\n')

def r2cgridfromfst(fstmatchgrid, r2c):

	# Set grid characteristics from the fst grid.
	# CMC/RPN uses 'Sphere' ellipsoid (historically).
	# Change lon to use -180->180 (if applicable).
	# Offset the points by half-delta as r2c files represent points between vertices of the grid.

	if (fstmatchgrid['grref'] == 'L'):
		r2c.grid.Projection = 'LATLONG'
		r2c.grid.Ellipsoid = 'SPHERE'
		r2c.grid.xOrigin = fstmatchgrid['lon0'] - fstmatchgrid['dlon']/2.0
		if (r2c.grid.xOrigin > 180.0):
			r2c.grid.xOrigin -= 360.0
		r2c.grid.yOrigin = fstmatchgrid['lat0'] - fstmatchgrid['dlat']/2.0
		r2c.grid.xCount = fstmatchgrid['ni']
		r2c.grid.yCount = fstmatchgrid['nj']
		r2c.grid.xDelta = fstmatchgrid['dlon']
		r2c.grid.yDelta = fstmatchgrid['dlat']
	elif (fstmatchgrid['grref'] == 'E'):
		r2c.grid.Projection = 'ROTLATLONG'
		r2c.grid.Ellipsoid = 'SPHERE'
		r2c.grid.xOrigin = fstmatchgrid['lon0'] - fstmatchgrid['dlon']/2.0
		r2c.grid.yOrigin = fstmatchgrid['lat0'] - fstmatchgrid['dlat']/2.0
		r2c.grid.CentreLatitude = fstmatchgrid['xlat1']
		r2c.grid.CentreLongitude = fstmatchgrid['xlon1']
		r2c.grid.RotationLatitude = fstmatchgrid['xlat2']
		r2c.grid.RotationLongitude = fstmatchgrid['xlon2']
		r2c.grid.xCount = fstmatchgrid['ni']
		r2c.grid.yCount = fstmatchgrid['nj']
		r2c.grid.xDelta = fstmatchgrid['dlon']
		r2c.grid.yDelta = fstmatchgrid['dlat']
	else:
		print('ERROR: The fst grid type ' + fstmatchgrid['grref'] + ' is not supported. The script cannot continue.')
		exit()

def r2cgridfromr2c(r2c, fpathr2cin):

	# Set r2c attributes to match the grid defined by fpathr2cin.

	with open(fpathr2cin, 'r') as f:
		for l in f:

			# Continue if not an attribute identified with leading ':'.

			if (l.find(':') != 0):
				continue

			# Identify and save desired keywords.

			m = l.strip().lower().split()
			if (m[0] == ':projection'):
                		r2c.grid.Projection = m[1].upper()
			if (m[0] == ':ellipsoid'):
		                r2c.grid.Ellipsoid = m[1].upper()
			if (m[0] == ':centrelatitude'):
		                r2c.grid.CentreLatitude = float(m[1])
			if (m[0] == ':centrelongitude'):
                		r2c.grid.CentreLongitude = float(m[1])
			if (m[0] == ':rotationlatitude'):
		                r2c.grid.RotationLatitude = float(m[1])
			if (m[0] == ':rotationlongitude'):
                		r2c.grid.RotationLongitude = float(m[1])
			if (m[0] == ':xorigin'):
				r2c.grid.xOrigin = float(m[1])
			if (m[0] == ':yorigin'):
				r2c.grid.yOrigin = float(m[1])
			if (m[0] == ':xcount'):
        			r2c.grid.xCount = int(m[1])
			if (m[0] == ':ycount'):
			        r2c.grid.yCount = int(m[1])
			if (m[0] == ':xdelta'):
			        r2c.grid.xDelta = float(m[1])
			if (m[0] == ':ydelta'):
			        r2c.grid.yDelta = float(m[1])
			if (m[0] == ':endheader'):
				return

def fstgridfromr2c(r2c):

	# Set grid fst characteristics from the r2c grid.
	# Change lon to use 0->360 (if applicable).
	# Reset the points by half-delta as r2c files represent points between vertices of the grid.

	if (r2c.grid.Projection.lower() == 'latlong'):
		lon0 = r2c.grid.xOrigin + r2c.grid.xDelta/2.0
		if (lon0 < 0.0):
			lon0 += 360.0
		lat0 = r2c.grid.yOrigin + r2c.grid.yDelta/2.0
		return rmn.defGrid_ZL(ni = r2c.grid.xCount, nj = r2c.grid.yCount, lat0 = lat0, lon0 = lon0, dlat = r2c.grid.yDelta, dlon = r2c.grid.xDelta)
	elif (r2c.grid.Projection.lower() == 'rotlatlong'):
		lon0 = r2c.grid.xOrigin + r2c.grid.xDelta/2.0
		lat0 = r2c.grid.yOrigin + r2c.grid.yDelta/2.0
		return rmn.defGrid_ZE(ni = r2c.grid.xCount, nj = r2c.grid.yCount, lat0 = lat0, lon0 = lon0, dlat = r2c.grid.yDelta, dlon = r2c.grid.xDelta, xlat1 = r2c.grid.CentreLatitude, xlon1 = r2c.grid.CentreLongitude, xlat2 = r2c.grid.RotationLatitude, xlon2 = r2c.grid.RotationLongitude)
	else:
		print('ERROR: The fst grid type ' + r2c.grid.Projection + ' is not supported. The script cannot continue.')
		exit()

def latlonvalfromfst(
	lat, lon, fstfid, fstnomvar, fstetiket = ' ', fstip1 = -1, fstip2 = -1, fstip3 = -1,
	intpopt = rmn.EZ_INTERP_NEAREST,
	constmul = 1.0, constadd = 0.0, constrmax = float('inf'), constrmin = float('-inf')):

	# Grab the field.
	# Returns 'None' if no field is found.
	# Use 'istat' to control return from special cases.

	istat = 0
	field = None
	fstvargrid = None

	# Set interpolation method.

	rmn.ezsetopt(rmn.EZ_OPT_INTERP_DEGREE, intpopt)

	# Special cases.

	# Wind components and wind speed and direction (grouped together).

	if (fstnomvar.lower() == 'uu' or fstnomvar.lower() == 'vv' or fstnomvar.lower() == 'uv' or fstnomvar.lower() == 'wd'):
		uu = rmn.fstlir(fstfid, nomvar = 'UU', etiket = fstetiket, ip1 = fstip1, ip2 = fstip2, ip3 = fstip3)
		vv = rmn.fstlir(fstfid, nomvar = 'VV', etiket = fstetiket, ip1 = fstip1, ip2 = fstip2, ip3 = fstip3)
		if (uu is None or vv is None):
			istat = -1
		else:
			fstvargrid = rmn.readGrid(fstfid, uu)
			xy = rmn.gdxyfll(fstvargrid, lat = lat, lon = lon)
			if (fstnomvar.lower() == 'uu' or fstnomvar.lower() == 'vv'):
				uuvv = rmn.gdxyvval(fstvargrid, xy['x'], xy['y'], uu['d'], vv['d'])
				if (fstnomvar.lower() == 'uu'):
					field = uuvv[0]
				else:
					field = uuvv[1]
			else:
				from gdxywdval import gdxywdval
				spdwd = gdxywdval(fstvargrid, xy['x'], xy['y'], uu['d'], vv['d'])
				if (fstnomvar.lower() == 'uv'):
					field = spdwd[0]
				else:
					field = spdwd[1]

	# Normal scalar interpolation.

	else:
		fstvar = rmn.fstlir(fstfid, nomvar = fstnomvar, etiket = fstetiket, ip1 = fstip1, ip2 = fstip2, ip3 = fstip3)
		if (fstvar is None):
			istat = -1
		else:
			fstvargrid = rmn.readGrid(fstfid, fstvar)
			xy = rmn.gdxyfll(fstvargrid, lat = lat, lon = lon)
			field = rmn.gdxysval(fstvargrid, xy['x'], xy['y'], fstvar['d'])

	# Check status.

	if (istat != 0 or field is None):
		print('ERROR: Unable to fetch field: %s. Attribute not appended. The script cannot continue.' % fstnomvar)
		exit()

	# Apply transforms.

	field = constmul*field + constadd
	field = np.clip(field, constrmin, constrmax)
	return field

def r2cattributefromfst(
	r2cattribute, fstmatchgrid, fstfid, fstnomvar, fstetiket = ' ', fstip1 = -1, fstip2 = -1, fstip3 = -1,
	intpopt = rmn.EZ_INTERP_NEAREST,
	constmul = 1.0, constadd = 0.0, constrmax = float('inf'), constrmin = float('-inf'), accfield = False):

	# Grab the field.
	# Returns 'None' if no field is found.
	# Use 'istat' to control return from special cases.

	istat = 0
	if (accfield and r2cattribute.AttributeData is None) or not accfield:
		r2cattribute.AttributeData = np.zeros((fstmatchgrid['ni'], fstmatchgrid['nj']))
	field = None
	fstvargrid = None

	# Set interpolation method.

	rmn.ezsetopt(rmn.EZ_OPT_INTERP_DEGREE, intpopt)

	# Special cases.

	# Wind components and wind speed and direction (grouped together).

	if (fstnomvar.lower() == 'uu' or fstnomvar.lower() == 'vv' or fstnomvar.lower() == 'uv' or fstnomvar.lower() == 'wd'):
		uu = rmn.fstlir(fstfid, nomvar = 'UU', etiket = fstetiket, ip1 = fstip1, ip2 = fstip2, ip3 = fstip3)
		vv = rmn.fstlir(fstfid, nomvar = 'VV', etiket = fstetiket, ip1 = fstip1, ip2 = fstip2, ip3 = fstip3)
		if (uu is None or vv is None):
			istat = -1
		else:
			fstvargrid = rmn.readGrid(fstfid, uu)
			rmn.ezdefset(fstmatchgrid, fstvargrid)
			if (fstnomvar.lower() == 'uu' or fstnomvar.lower() == 'vv'):
				uuvv = rmn.ezuvint(fstmatchgrid, fstvargrid, uu['d'], vv['d'])
				if (fstnomvar.lower() == 'uu'):
					field = uuvv[0]
				else:
					field = uuvv[1]
			else:
				from ezwdint import ezwdint
				spdwd = ezwdint(fstmatchgrid, fstvargrid, uu['d'], vv['d'])
				if (fstnomvar.lower() == 'uv'):
					field = spdwd[0]
				else:
					field = spdwd[1]
			rmn.gdrls(fstvargrid)

	# Normal scalar interpolation.

	else:
		fstvar = rmn.fstlir(fstfid, nomvar = fstnomvar, etiket = fstetiket, ip1 = fstip1, ip2 = fstip2, ip3 = fstip3)
		if (fstvar is None):
			istat = -1
		else:
			fstvargrid = rmn.readGrid(fstfid, fstvar)
			rmn.ezdefset(fstmatchgrid, fstvargrid)
			field = rmn.ezsint(fstmatchgrid, fstvargrid, fstvar['d'])
			rmn.gdrls(fstvargrid)

	# Check status.

	if (istat != 0):
		print('ERROR: Unable to fetch field: %s. Attribute not appended. The script cannot continue.' % fstnomvar)
		exit()

	# Apply transforms.

	field = constmul*field + constadd
	field = np.clip(field, constrmin, constrmax)
	r2cattribute.AttributeData += field
