#!/usr/bin/python

# Import base pacakges.
from os import path
from time import gmtime, strftime, mktime
from datetime import datetime
import shlex
import numpy as np
import pandas as pd

# Import rpnpy if the library exists.
# To load rpnpy (ECCC environment):
# . s.ssmuse.dot ENV/py/2.7/rpnpy/2.0.4
RUNRPNPY = True
try:
	import rpnpy.librmn.all as rmn
except:
	print('REMARK: The rpnpy library cannot be loaded or is not found. Standard file (fst) file processing is disabled.')
	class rmn_f(object):
		def __call__(self, *args, **kwargs):
			return None
	class rmn_z(object):
		def __getattr__(self, attr):
			return rmn_f()
		def __setattr__(self, attr, val):
			pass
	rmn = rmn_z()
	RUNRPNPY = False

# Structures.
# Variable structures used across routines.

# Meta information listed in drainage database files.
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

# Generic structure for EnSim/GreenKenue projection.
class r2cgrid(object):
	def __init__(self):

		# Standard EnSim attributes.
		self.Projection = 'UNKNOWN'
		self.Ellipsoid = 'UNKNOWN'
		self.xOrigin = 0.0
		self.yOrigin = 0.0
		self.xCount = 0
		self.yCount = 0
		self.xDelta = 0.0
		self.yDelta = 0.0

		# Compliancy terms to avoid rederivation for netCDF projection (not part of EnSim standard).
		# Note: These omit the half-delta offset.
		self.GridNorthPoleLatitude = 0.0
		self.GridNorthPoleLongitude = 0.0
		self.NorthPoleGridLongitude = 0.0

# Generic structure for attribute data.
class r2cattribute(object):
	def __init__(self, AttributeName = None, AttributeType = None, AttributeUnits = None, AttributeData = None):
		self.AttributeName = AttributeName
		self.AttributeType = AttributeType
		self.AttributeUnits = AttributeUnits
		self.AttributeData = AttributeData
		self.FrameCount = 0

# Generic structure for 'r2c' file format.
class r2cfile(object):
	def __init__(self):
		self.meta = None
		self.grid = r2cgrid()
		self.attr = []

# Meta information listed in tb0 format files.
class tb0meta(object):
	def __init__(self):
		self.StartTime = None
		self.DeltaT = 0.0
		self.RoutingDeltaT = 0.0
		self.FillFlag = ''

# Generic structure for column data.
class tb0column(object):
	def __init__(self, ColumnName = None, ColumnType = None, ColumnUnits = None, ColumnLocationX = None, ColumnLocationY = None):
		self.ColumnName = ColumnName
		self.ColumnType = ColumnType
		self.ColumnUnits = ColumnUnits
		self.ColumnLocationX = ColumnLocationX
		self.ColumnLocationY = ColumnLocationY
		self.ColumnData = None

# Generic structure for 'tb0' file format.
class tb0file(object):
	def __init__(self):
		self.meta = None
		self.proj = r2cgrid()
		self.cols = []
		self.RecordCount = 0

# Generic structure for conversion field ('fst' to 'r2c').
# This structure is only used with standard file (fst) format.
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

# Generic structure for conversion field ('fst' to CSV list or 'tb0').
# This structure is only used with standard file (fst) format.
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

# Routines.
# File manipulation routines.

# Open and print the header to file using information provided via 'r2c'.
# Overwrites any existing file with the same file information.
# Supports 'r2c' format files with and without drainage database meta information.
# Supports 'LATLONG' and 'ROTLATLONG' projections.
def r2cfilecreateheader(r2c, fpathr2cout):

	# Write the header.
	# Writing the header overwrites any existing file.
	with open(fpathr2cout, 'w') as r2cfid:

		# Write the file type.
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

		# Write meta information is provided in the 'r2c' object.
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

		# Write the projection.
		if (r2c.grid.Projection == 'LATLONG'):

			# 'LATLONG'.
			r2cfid.write(':Projection ' + r2c.grid.Projection + '\n')
			r2cfid.write(':Ellipsoid ' + r2c.grid.Ellipsoid + '\n')
		elif (r2c.grid.Projection == 'ROTLATLONG'):

			# 'ROTLATLONG'.
			r2cfid.write(':Projection ' + r2c.grid.Projection + '\n')
			r2cfid.write(':CentreLatitude ' + str(r2c.grid.CentreLatitude) + '\n')
			r2cfid.write(':CentreLongitude ' + str(r2c.grid.CentreLongitude) + '\n')
			r2cfid.write(':RotationLatitude ' + str(r2c.grid.RotationLatitude) + '\n')
			r2cfid.write(':RotationLongitude ' + str(r2c.grid.RotationLongitude) + '\n')
			r2cfid.write(':Ellipsoid ' + r2c.grid.Ellipsoid + '\n')

		# Write the grid origin.
		r2cfid.write('#\n')
		r2cfid.write(':xOrigin ' + str(r2c.grid.xOrigin) + '\n')
		r2cfid.write(':yOrigin ' + str(r2c.grid.yOrigin) + '\n')
		r2cfid.write('#\n')
		if (r2c.grid.Projection == 'ROTLATLONG'):

			# Compliancy terms to avoid rederivation for netCDF projection (not part of EnSim standard).
			# Note: These omit the half-delta offset.
			r2cfid.write(':GridNorthPoleLatitude ' + str(r2c.grid.GridNorthPoleLatitude) + '\n')
			r2cfid.write(':GridNorthPoleLongitude ' + str(r2c.grid.GridNorthPoleLongitude) + '\n')
			r2cfid.write(':NorthPoleGridLongitude ' + str(r2c.grid.NorthPoleGridLongitude) + '\n')
		r2cfid.write('#\n')

		# Write the list of attributes (multi-frame or single).
		# A generic description is created in the absence of 'AttributeName'.
		# Optional specifications, such as 'AttributeType' and 'AttributeUnits', are omitted if empty.
		for i, a in enumerate(r2c.attr):
			if (not a.AttributeName is None):
				attribute_name = a.AttributeName
			else:
				attribute_name = 'Attribute' + str(i + 1)
			if (' ' in attribute_name):
				attribute_name = '\"' + attribute_name + '\"'
			r2cfid.write(':AttributeName ' + str(i + 1) + ' ' + attribute_name + '\n')
			if (not a.AttributeType is None):
				r2cfid.write(':AttributeType ' + str(i + 1) + ' ' + a.AttributeType + '\n')
			if (not a.AttributeUnits is None):
				r2cfid.write(':AttributeUnits ' + str(i + 1) + ' ' + a.AttributeUnits + '\n')

		# Write the dimension specification of the grid.
		r2cfid.write('#\n')
		r2cfid.write(':xCount ' + str(r2c.grid.xCount) + '\n')
		r2cfid.write(':yCount ' + str(r2c.grid.yCount) + '\n')
		r2cfid.write(':xDelta ' + str(r2c.grid.xDelta) + '\n')
		r2cfid.write(':yDelta ' + str(r2c.grid.yDelta) + '\n')
		r2cfid.write('#\n')
		r2cfid.write('#\n')

		# End of header.
		r2cfid.write(':EndHeader\n')

# Append single-frame attributes to an 'r2c' format file (instantaneous).
# Appends records to an existing file.
# 'r2cfilecreateheader' should be called in advance of this routine to properly create the file.
# The file can contain multiple attributes.
# File operation re-opens and appends to the file to reduce memory usage.
def r2cfileappendattributes(r2c, fpathr2cout):

	# Data frame (single-frame, no ':Frame'/':EndFrame' wrapper.
	# Will append to existing file.
	with open(fpathr2cout, 'a') as r2cfid:
		for i, a in enumerate(r2c.attr):
			if (not a.AttributeName is None):
				print('Saving ... ' + a.AttributeName)
			else:
				print('Saving ... Attribute ' + str(i + 1))
			for r in np.transpose(a.AttributeData):
				r2cfid.write(' '.join(r.astype(str)) + '\n')

# Append multi-frame attributes to an 'r2c' format file (time-series).
# Appends records to an existing file.
# 'r2cfilecreateheader' should be called in advance of this routine to properly create the file.
# The file should contain only 1 attribute (if multiple attributes exist, only the first is used).
# File operation re-opens and appends to the file to reduce memory usage.
def r2cfileappendmultiframe(r2c, fpathr2cout, frameno, frametime):

	# Data frame (multi-frame, with ':Frame'/':EndFrame' wrapper.
	# Will append to existing file.
	# Standard date format for 'r2c'/EnSim formats: "yyyy/MM/dd HH:mm:ss.SSS".
	r2c.attr[0].FrameCount += 1
	frameno = r2c.attr[0].FrameCount
	with open(fpathr2cout, 'a') as r2cfid:
		r2cfid.write(':Frame %d %d \"%s\"\n' % (frameno, frameno, strftime('%Y/%m/%d %H:%M:%S', frametime.timetuple())))
		for r in np.transpose(r2c.attr[0].AttributeData):
			r2cfid.write(' '.join(r.astype(str)) + '\n')
		r2cfid.write(':EndFrame\n')

# Open and print the header to file using information provided via 'tb0'.
# Overwrites any existing file with the same file information.
# Supports 'LATLONG' projection only.
def tb0filecreateheader(tb0, fpathtb0out):

	# Write the header.
	# Writing the header overwrites any existing file.
	with open(fpathtb0out, 'w') as tb0fid:

		# Write the file type.
		tb0fid.write('########################################\n')
		tb0fid.write(':FileType tb0 ASCII EnSim 1.0\n')
		tb0fid.write('#\n')
		tb0fid.write('# DataType EnSim Table\n')
		tb0fid.write('#\n')
		tb0fid.write(':Application ensim_utils.py\n')
		tb0fid.write(':Version 1.0\n')
		tb0fid.write(':WrittenBy ensim_utils.py\n')
		tb0fid.write(':CreationDate ' + strftime('%Y/%m/%d %H:%M:%S', gmtime()) + '\n')
		tb0fid.write('#\n')
		tb0fid.write('#---------------------------------------\n')
		tb0fid.write('#\n')

		# Write meta information is provided in the 'tb0' object.
		# Standard date format for EnSim/Green Kenue formats: "yyyy/MM/dd HH:mm:ss.SSS".
		if (not tb0.meta is None):
			tb0fid.write('#\n')
			tb0fid.write(':StartTime ' + strftime('%Y/%m/%d %H:%M:%S', tb0.meta.StartTime.timetuple()) + '\n')
			tb0fid.write(':DeltaT ' + str(tb0.meta.DeltaT) + '\n')
			tb0fid.write(':RoutingDeltaT ' + str(tb0.meta.RoutingDeltaT) + '\n')
			tb0fid.write('#\n')
			tb0fid.write(':FillFlag ' + tb0.meta.FillFlag + '\n')
		tb0fid.write('#\n')

		# Write the projection.
		if (tb0.proj.Projection == 'LATLONG'):

			# 'LATLONG'.
			tb0fid.write(':Projection ' + tb0.proj.Projection + '\n')
			tb0fid.write(':Ellipsoid ' + tb0.proj.Ellipsoid + '\n')
		tb0fid.write('#\n')

		# Write meta information of the columns.
		# A generic ID is created in the absence of 'ColumnName'.
		# Optional specifications, such as 'ColumnType' and 'ColumnUnits', print the EnSim/Green Kenue default if empty.
		# Multiple columns are written as a row.
		tb0fid.write(':ColumnMetaData\n')
		line = ':ColumnName'
		for i, a in enumerate(tb0.cols):
			if (not a.ColumnName is None):
				if (' ' in a.ColumnName):
					line += ' \"' + a.ColumnName + '\"'
				else:
					line += ' ' + a.ColumnName
			else:
				line += ' ' + str(i + 1)
		tb0fid.write(line + '\n')
		line = ':ColumnType'
		for i, a in enumerate(tb0.cols):
			if (not a.ColumnType is None):
				line += ' ' + a.ColumnType
			else:
				line += ' float'
		tb0fid.write(line + '\n')
		line = ':ColumnUnits'
		for i, a in enumerate(tb0.cols):
			if (not a.ColumnUnits is None):
				if (' ' in a.ColumnUnits):
					line += ' \"' + a.ColumnUnits + '\"'
				else:
					line += ' ' + a.ColumnUnits
			else:
				line += ' none'
		tb0fid.write(line + '\n')
		line = ':ColumnLocationX'
		for i, a in enumerate(tb0.cols):
			line += ' ' + str(a.ColumnLocationX)
		tb0fid.write(line + '\n')
		line = ':ColumnLocationY'
		for i, a in enumerate(tb0.cols):
			line += ' ' + str(a.ColumnLocationY)
		tb0fid.write(line + '\n')
		tb0fid.write(':EndColumnMetaData\n')
		tb0fid.write('#\n')

		# End of header.
		tb0fid.write(':EndHeader\n')

# Append data to a 'tb0' format file (time-series).
# Appends records to an existing file.
# 'r2cfilecreateheader' should be called in advance of this routine to properly create the file.
# File operation re-opens and appends to the file to reduce memory usage.
def tb0fileappendcolumndata(tb0, fpathtb0out):

	# Will append the data to an existing file.
	# Determine formatting by the type of variable (%g).
	with open(fpathtb0out, 'a') as tb0fid:
		for n in range(tb0.RecordCount):
			line = ''
			for i, a in enumerate(tb0.cols):
				line += ' ' + str(a.ColumnData[n])
			tb0fid.write(line + '\n')

# Derive the 'r2c'/EnSim compatible grid specification from an existing standard format (fst) file.
# Supports 'LATLONG' and 'ROTLATLONG' projections.
# Derives the projection from the passed 'fstmatchgrid' object.
def r2cgridfromfst(fstmatchgrid, r2c):

	# Check for 'RUNRPNPY'.
	if (not RUNRPNPY):
		print('ERROR: rpnpy is not loaded. Function cannot continue: ' % 'r2cgridfromfst')
		exit()

	# Set grid characteristics from the fst grid.
	# CMC/RPN uses 'Sphere' ellipsoid (historically).
	# Change lon to use -180->180 (if applicable).
	# Offset the points by half-delta as r2c files represent points between vertices of the grid.
	if (fstmatchgrid['grref'] == 'L'):

		# Type 'L': EnSim 'LATLONG'
		r2c.grid.Projection = 'LATLONG'
		r2c.grid.Ellipsoid = 'SPHERE'
		r2c.grid.xOrigin = fstmatchgrid['lon0'] - fstmatchgrid['dlon']/2.0
		if (r2c.grid.xOrigin > 180.0):

			# Convert range from (0->360) to (-180->180).
			# Should not be necessary, but left here in case existing scripts use this assumption.
			r2c.grid.xOrigin -= 360.0
		r2c.grid.yOrigin = fstmatchgrid['lat0'] - fstmatchgrid['dlat']/2.0
		r2c.grid.xCount = fstmatchgrid['ni']
		r2c.grid.yCount = fstmatchgrid['nj']
		r2c.grid.xDelta = fstmatchgrid['dlon']
		r2c.grid.yDelta = fstmatchgrid['dlat']
	elif (fstmatchgrid['grref'] == 'E'):

		# Type 'E': EnSim 'ROTLATLONG'.
		r2c.grid.Projection = 'ROTLATLONG'
		r2c.grid.Ellipsoid = 'SPHERE'
		r2c.grid.xOrigin = fstmatchgrid['rlon0'] - fstmatchgrid['dlon']/2.0
		r2c.grid.yOrigin = fstmatchgrid['rlat0'] - fstmatchgrid['dlat']/2.0
		r2c.grid.CentreLatitude = fstmatchgrid['xlat1']
		r2c.grid.CentreLongitude = fstmatchgrid['xlon1']
		r2c.grid.RotationLatitude = fstmatchgrid['xlat2']
		r2c.grid.RotationLongitude = fstmatchgrid['xlon2']
		r2c.grid.xCount = fstmatchgrid['ni']
		r2c.grid.yCount = fstmatchgrid['nj']
		r2c.grid.xDelta = fstmatchgrid['dlon']
		r2c.grid.yDelta = fstmatchgrid['dlat']

		# Compliancy terms to avoid rederivation for netCDF projection (not part of EnSim standard).
		# Note: These omit the half-delta offset.
		r2c.grid.GridNorthPoleLatitude = fstmatchgrid['lat0']
		r2c.grid.GridNorthPoleLongitude = fstmatchgrid['lon0']
		r2c.grid.NorthPoleGridLongitude = 0.0
	else:

		# Unsupported projection.
		print('ERROR: The fst grid type ' + fstmatchgrid['grref'] + ' is not supported. The script cannot continue.')
		exit()

# Derive the 'r2c'/EnSim compatible grid specification from an existing 'r2c' format file.
# Supports 'LATLONG' and 'ROTLATLONG' projections.
# Reads the projection from file.
def r2cgridfromr2c(r2c, fpathr2cin):

	# Set r2c attributes to match the grid defined by fpathr2cin.
	# Reads the projection from file.
	with open(fpathr2cin, 'r') as f:
		for l in f:

			# Continue if not an attribute identified with leading ':'.
			if (l.find(':') != 0):
				continue

			# Identify and save attributes related to projection and grid specification.
			m = l.strip().lower().split()

			# Standard EnSim attributes (LATLONG, ROTLATLONG).
			if (m[0] == ':projection'):
				r2c.grid.Projection = m[1].upper()
			elif (m[0] == ':ellipsoid'):
				r2c.grid.Ellipsoid = m[1].upper()
			elif (m[0] == ':centrelatitude'):
				r2c.grid.CentreLatitude = float(m[1])
			elif (m[0] == ':centrelongitude'):
				r2c.grid.CentreLongitude = float(m[1])
			elif (m[0] == ':rotationlatitude'):
				r2c.grid.RotationLatitude = float(m[1])
			elif (m[0] == ':rotationlongitude'):
				r2c.grid.RotationLongitude = float(m[1])
			elif (m[0] == ':xorigin'):
				r2c.grid.xOrigin = float(m[1])
			elif (m[0] == ':yorigin'):
				r2c.grid.yOrigin = float(m[1])
			elif (m[0] == ':xcount'):
				r2c.grid.xCount = int(m[1])
			elif (m[0] == ':ycount'):
				r2c.grid.yCount = int(m[1])
			elif (m[0] == ':xdelta'):
				r2c.grid.xDelta = float(m[1])
			elif (m[0] == ':ydelta'):
				r2c.grid.yDelta = float(m[1])

			# Compliancy terms to avoid rederivation for netCDF projection (not part of EnSim standard).
			# Note: These omit the half-delta offset.
			elif (m[0] == ':gridnorthpolelatitude'):
				r2c.grid.GridNorthPoleLatitude = float(m[1])
			elif (m[0] == ':gridnorthpolelongitude'):
				r2c.grid.GridNorthPoleLongitude = float(m[1])
			elif (m[0] == ':northpolegridlongitude'):
				r2c.grid.NorthPoleGridLongitude = float(m[1])

			# ':EndHeader'.
			elif (m[0] == ':endheader'):

				# Exit if at the end of the header.
				return

# Derive the EnSim/Green Kenue projection from an existing 'tb0' format file.
# Supports 'LATLONG' projection only.
def tb0projectionfromtb0(tb0, fpathtb0in):

	# Set tb0 attributes to match the projection defined in fpathtb0in.
	with open(fpathtb0in, 'r') as f:
		for l in f:

			# Continue if not an attribute identified with leading ':'.
			if (l.find(':') != 0):
				continue

			# Identify and save attributes related to projection and grid specification.
			m = l.strip().lower().split()
			if (m[0] == ':projection'):
				tb0.proj.Projection = m[1].upper()
			elif (m[0] == ':ellipsoid'):
				tb0.proj.Ellipsoid = m[1].upper()
			elif (m[0] == ':endheader'):

				# Exit if at the end of the header.
				return

	# Stop with an error if the projection is unsupported.
	if (tb0.proj.Projection != 'LATLONG'):
		print('ERROR: The projection ' + tb0.proj.Projection + ' is not supported. The script cannot continue.')
		exit()

# Derive drainage database meta information from an existing 'r2c' format file.
# Reads the information from file.
def r2cmetafromr2c(r2c, fpathr2cin):

	# Set r2c attributes baesd on the attributes in fpathr2cin.
	# Reads the information from file.
	r2c.meta = r2cmeta()
	with open(fpathr2cin, 'r') as f:
		for l in f:

			# Continue if not an attribute identified with leading ':'.
			if (l.find(':') != 0):
				continue

			# Identify and save attributes related to meta information.
			m = l.strip().lower().split()
			if(m[0] == ':nominalgridsize_al'):
				r2c.meta.NominalGridSize_AL = float(m[1])
			elif(m[0] == ':contourinterval'):
				r2c.meta.ContourInterval = float(m[1])
			elif(m[0] == ':imperviousarea'):
				r2c.meta.ImperviousArea = float(m[1])
			elif(m[0] == ':classcount'):
				r2c.meta.ClassCount = int(m[1])
			elif(m[0] == ':numriverclasses'):
				r2c.meta.NumRiverClasses = int(m[1])
			elif(m[0] == ':elevconversion'):
				r2c.meta.ElevConversion = float(m[1])
			elif(m[0] == ':totalnumofgrids'):
				r2c.meta.TotalNumOfGrids = int(m[1])
			elif(m[0] == ':numgridsinbasin'):
				r2c.meta.NumGridsInBasin = int(m[1])
			elif(m[0] == ':debuggridno'):
				r2c.meta.DebugGridNo = int(m[1])
			elif (m[0] == ':endheader'):

				# Exit if at the end of the header.
				return

# Derive the standard file (fst)/RPN format grid specification from an existing 'r2c' format file.
# Supports 'LATLONG' and 'ROTLATLONG' projections.
# Derives the projection from attributes of the passed 'r2c' object.
def fstgridfromr2c(r2c):

	# Check for 'RUNRPNPY'.
	if (not RUNRPNPY):
		print('ERROR: rpnpy is not loaded. Function cannot continue: ' % 'fstgridfromr2c')
		exit()

	# Set grid fst characteristics from the r2c grid.
	# Change lon to use 0->360 (if applicable).
	# Reset the points by half-delta as r2c files represent points between vertices of the grid.
	if (r2c.grid.Projection.lower() == 'latlong'):

		# 'LATLONG' projection to 'L' type (ZL).
		# Offset the points by half-delta to convert from the 'r2c' matrix to the actual data points.
		lon0 = r2c.grid.xOrigin + r2c.grid.xDelta/2.0
		if (lon0 < 0.0):
			lon0 += 360.0
		lat0 = r2c.grid.yOrigin + r2c.grid.yDelta/2.0
		return rmn.defGrid_ZL(ni = r2c.grid.xCount, nj = r2c.grid.yCount, lat0 = lat0, lon0 = lon0, dlat = r2c.grid.yDelta, dlon = r2c.grid.xDelta)
	elif (r2c.grid.Projection.lower() == 'rotlatlong'):

		# 'ROTLATLONG' projection to 'E' type (ZE).
		# Offset the points by half-delta to convert from the 'r2c' matrix to the actual data points.
		rlon0 = r2c.grid.xOrigin + r2c.grid.xDelta/2.0
		rlat0 = r2c.grid.yOrigin + r2c.grid.yDelta/2.0
		(lat0, lon0) = rmn.egrid_rll2ll(xlat1 = r2c.grid.CentreLatitude, xlon1 = r2c.grid.CentreLongitude, xlat2 = r2c.grid.RotationLatitude, xlon2 = r2c.grid.RotationLongitude, rlat = rlat0, rlon = rlon0)
		return rmn.defGrid_ZE(ni = r2c.grid.xCount, nj = r2c.grid.yCount, lat0 = lat0, lon0 = lon0, dlat = r2c.grid.yDelta, dlon = r2c.grid.xDelta, xlat1 = r2c.grid.CentreLatitude, xlon1 = r2c.grid.CentreLongitude, xlat2 = r2c.grid.RotationLatitude, xlon2 = r2c.grid.RotationLongitude)
	else:

		# Unknown projection.
		print('ERROR: The fst grid type ' + r2c.grid.Projection + ' is not supported. The script cannot continue.')
		exit()

# Read meta information from an existing 'tb0' format file.
def tb0metafromtb0(tb0, fpathtb0in):

	# Set tb0 attributes based on the attributes in fpathtb0in.
	# Reads the information from file.
	tb0.meta = tb0meta()
	with open(fpathtb0in, 'r') as f:
		for l in f:

			# Continue if not an attribute identified with leading ':'.
			if (l.find(':') != 0):
				continue

			# Identify and save attributes related to meta information.
			m = l.strip().lower().split()
			if(m[0] == ':starttime'):
				tb0.meta.StartTime = datetime.strptime(' '.join(m[1:]).strip('"'), '%Y/%m/%d %H:%M:%S')
			elif(m[0] == ':deltat'):
				if (not m[1].find(':') == 0):
					tb0.meta.DeltaT = int(m[1])
				else:
					tb0.meta.DeltaT = datetime.strptime(m[1], '%H:%M:%S')
			elif(m[0] == ':routingdeltat'):
				if (not m[1].find(':') == 0):
					tb0.meta.RoutingDeltaT = int(m[1])
				else:
					tb0.meta.RoutingDeltaT = datetime.strptime(m[1], '%H:%M:%S')
			elif(m[0] == ':fillflag'):
				tb0.meta.FillFlag = m[1]
			elif (m[0] == ':endheader'):

				# Exit if at the end of the header.
				return

# Return a vector of point data read from standard file (fst) format.
# Check for special 'UU', 'VV', 'UV', or 'WD' attributes to for special wind-component interpolation.
# Use regular 'ez' interpolation for all other fields.
# Optionally, apply transform as prescribed by provided arguments.
# Calls 'exit()' if an error occurs while extracting the field.
def latlonvalfromfst(
	lat, lon, fstfid, fstnomvar, fstetiket = ' ', fstip1 = -1, fstip2 = -1, fstip3 = -1,
	intpopt = rmn.EZ_INTERP_NEAREST,
	constmul = 1.0, constadd = 0.0, constrmax = float('inf'), constrmin = float('-inf')):

	# Check for 'RUNRPNPY'.
	if (not RUNRPNPY):
		print('ERROR: rpnpy is not loaded. Function cannot continue: ' % 'tb0fromfst')
		exit()

	# Grab the field.
	# Returns 'None' if no field is found.
	# Use 'istat' to control return from special cases.
	istat = 0
	field = None
	fstvargrid = None

	# Set interpolation method.
	rmn.ezsetopt(rmn.EZ_OPT_INTERP_DEGREE, intpopt)

	# Extract the field and interpolate.
	if (fstnomvar.lower() == 'uu' or fstnomvar.lower() == 'vv' or fstnomvar.lower() == 'uv' or fstnomvar.lower() == 'wd'):

		# Special case: Wind components and wind speed and direction (grouped together).
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
	else:

		# Normal scalar interpolation.
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

# Return an array of gridded data read from standard file (fst) format.
# Check for special 'UU', 'VV', 'UV', or 'WD' attributes to for special wind-component interpolation.
# Use regular 'ez' interpolation for all other fields.
# Optionally, apply transform as prescribed by provided arguments.
# Optionally, preserve and add the extracted transformed field to existing data in the 'r2c' attribute if 'accfield' is 'True'.
# Calls 'exit()' if an error occurs while extracting the field.
def r2cattributefromfst(
	r2cattribute, fstmatchgrid, fstfid, fstnomvar, fstetiket = ' ', fstip1 = -1, fstip2 = -1, fstip3 = -1,
	intpopt = rmn.EZ_INTERP_NEAREST,
	constmul = 1.0, constadd = 0.0, constrmax = float('inf'), constrmin = float('-inf'), accfield = False):

	# Check for 'RUNRPNPY'.
	if (not RUNRPNPY):
		print('ERROR: rpnpy is not loaded. Function cannot continue: ' % 'r2cattributefromfst')
		exit()

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

	# Extract the field and interpolate.
	if (fstnomvar.lower() == 'uu' or fstnomvar.lower() == 'vv' or fstnomvar.lower() == 'uv' or fstnomvar.lower() == 'wd'):

		# Special case: Wind components and wind speed and direction (grouped together).
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
	else:

		# Normal scalar interpolation.
		fstvar = rmn.fstlir(fstfid, nomvar = fstnomvar, etiket = fstetiket, ip1 = fstip1, ip2 = fstip2, ip3 = fstip3)
		if (fstvar is None):
			istat = -1
		else:
			fstvargrid = rmn.readGrid(fstfid, fstvar)
			rmn.ezdefset(fstmatchgrid, fstvargrid)
			field = rmn.ezsint(fstmatchgrid, fstvargrid, fstvar['d'])

	# Check status.
	if (istat != 0):
		print('ERROR: Unable to fetch field: %s. Attribute not appended. The script cannot continue.' % fstnomvar)
		exit()

	# Apply transforms.
	field = constmul*field + constadd
	field = np.clip(field, constrmin, constrmax)
	r2cattribute.AttributeData += field

# Populate attributes from an existing 'r2c' format file.
# Reads the attributes from file.
# 'r2cgridfromr2c' should be called in advance of this routine to read the grid specification of the file.
def r2cattributesfromr2c(r2c, fpathr2cin):

	# Attribute count.
	a = 0

	# Set r2c attributes to match the grid defined by fpathr2cin.
	# Reads the projection from file.
	with open(fpathr2cin, 'r') as f:

		# Read attribute information from the header.
		in_header = True
		while True:

			# Read line and break if no more lines exist in the file.
			l = f.readline()
			if not l:
				break

			# Continue if not an attribute identified with leading ':'.
			if (l.find(':') != 0):
				continue

			# Check for 'AttributeName', which defines a new attribute.
			# Use the attribute index to assign 'AttributeType' and 'AttributeUnits' (to accommodate bad attribute indexing).
			# Attribute properties should always follow 'AttributeName', so assign them to the last activated attribute.
			m = l.strip().split()
			if (m[0].lower() == ':attributename'):
				a += 1
				r2c.attr.append(r2cattribute())

				# Multi-frame 'r2c' files, which should contain a single attribute, may not include an attribute ID.
				# Attribute properties should always follow 'AttributeName', so assign them to the last activated attribute (a - 1).
				if (len(m) > 1):
					if (m[1].isdigit() and len(m) > 2):
						r2c.attr[a - 1].AttributeName = ' '.join(m[2:])
					else:
						r2c.attr[a - 1].AttributeName = ' '.join(m[1:])
			elif (m[0].lower() == ':attributetype'):
				if (len(m) > 1):
					if (m[1].isdigit() and len(m) > 2):
						r2c.attr[a - 1].AttributeType = m[2]
					else:
						r2c.attr[a - 1].AttributeType = m[1]
			elif (m[0].lower() == ':attributeunits'):
				if (len(m) > 1):
					if (m[1].isdigit() and len(m) > 2):
						r2c.attr[a - 1].AttributeUnits = m[2]
					else:
						r2c.attr[a - 1].AttributeUnits = m[1]
			elif (m[0].lower() == ':endheader'):

				# Break if at the end of the header.
				break

		# Determine the type of file (single- or multi-frame).
		# Check for ':Frame' signature.
		# Backspace after the check to read data from the file.
		is_framed = True
		p = f.tell()
		l = f.readline()
		if (len(l) >= 6 and l.lower()[:6] == ':frame'):
			is_framed = True

			# Change the structure of 'AttributeData'.
			r2c.attr[0].AttributeData = pd.DataFrame(columns = ['Datetime', 'Values'])
			r2c.attr[0].AttributeData.set_index('Datetime', inplace = True)
		else:
			is_framed = False
		f.seek(p)

		# Read attributes from the file.
		if (is_framed):

			# Multi-frame file.
			# Each record is bounded by ':Frame'/':EndFrame' line markers, where ':Frame' marker also contains time-stamp of the record.
			while True:

				# Read line and break if no more lines exist in the file.
				l = f.readline()
				if not l:
					break

				# Parse the time-stamp from the ':Frame' marker.
				frame_mark = datetime.strptime(l.strip().lower().split('"')[1].split('.')[0], '%Y/%m/%d %H:%M:%S')

				# Read the data and increment the frame count.
				frame_data = np.fromfile(f, count = r2c.grid.yCount*r2c.grid.xCount, sep = ' ').reshape(r2c.grid.yCount, r2c.grid.xCount).transpose()

				# Read the ':EndFrame' marker.
				f.readline()

				# Append the record to the data frame.
				r2c.attr[0].AttributeData.loc[frame_mark] = [frame_data]

				# Increment the frame count.
				r2c.attr[0].FrameCount += 1
		else:

			# Single-frame file.
			# No markers exist between frames.
			# Enumerate over the expected number of attributes.
			for i, a in enumerate(r2c.attr):
				a.AttributeData = np.fromfile(f, count = r2c.grid.yCount*r2c.grid.xCount, sep = ' ').reshape(r2c.grid.yCount, r2c.grid.xCount).transpose()

# Populate columns from an existing 'tb0' format file.
# Reads the columns and data from file.
def tb0columnsfromtb0(tb0, fpathtb0in):

	# Column count.
	a = 0

	# Set tb0 attributes from the columns defined in fpathtb0in.
	with open(fpathtb0in, 'r') as f:

		# First, scan the number of columns in the file.
		n = 0
		while True:

			# Read line and break if no more lines exist in the file.
			l = f.readline()
			if not l:
				break

			# Continue if not an attribute identified with leading ':'.
			if (l.find(':') != 0):
				continue

			# Read the number of columns from applicable attributes.
			# Print a warning if the number of columns is not consistent.
			m = shlex.split(l.strip())
			if (m[0].lower() == ':columnname' or m[0].lower() == 'columntype' or m[0].lower() == 'columnunits' or m[0].lower() == 'columnlocationx' or m[0].lower() == 'columnlocationy'):
				if (n == 0):

					# Update the number of columns to the number of columns in this attribute.
					n = len(m) - 1
				else:
					if (not (len(m) - 1) == n):

						# Print a warning if the number of columns in this attribute does not match the number of columns derived from other attributes.
						print('WARNING: The number of columns (%d) in the %s attribute is different from the number of columns (%d) derived from other attributes.' % (len(m) - 1), m[0], n)
					if ((len(m) - 1) < n):

						# Print a warning if the number of columns in this attribute is less than the number of columns derived from other attributes.
						# Adjust the number of columns to be the lesser number.
						print('WARNING: The number of columns (%d) derived from other attributes is adjusted to the lesser number of columns (%d) in the %s attribute.' % n, (len(m) - 1), m[0])
						n = len(m) - 1
			elif (m[0].lower() == ':endheader'):

				# Break if at the end of the header.
				break

		# Stop with an error if no columns were found in the file.
		if (n == 0):
			print('ERROR: No columns were found in the file.')
			quit()
		else:
			tb0.cols = []
			for i in range(n):
				tb0.cols.append(tb0column())
				tb0.cols[i].ColumnData = []

		# Read the column meta information from the header.
		f.seek(0, 0)
		while True:

			# Read line and break if no more lines exist in the file.
			l = f.readline()
			if not l:
				break

			# Continue if not an attribute identified with leading ':'.
			if (l.find(':') != 0):
				continue

			# Assign the column meta information.
			# Columns were already added to the list from the scan.
			m = shlex.split(l.strip())
			if (m[0].lower() == ':columnname'):
				for i in range(n):
					tb0.cols[i].ColumnName = m[i + 1]
			elif (m[0].lower() == ':columntype'):
				for i in range(n):
					tb0.cols[i].ColumnType = m[i + 1]
			elif (m[0].lower() == ':columnunits'):
				for i in range(n):
					tb0.cols[i].ColumnUnits = m[i + 1]
			elif (m[0].lower() == ':columnlocationx'):
				for i in range(n):
					tb0.cols[i].ColumnLocationX = float(m[i + 1])
			elif (m[0].lower() == ':columnlocationy'):
				for i in range(n):
					tb0.cols[i].ColumnLocationY = float(m[i + 1])
			elif (m[0].lower() == ':endheader'):

				# Break if at the end of the header.
				break

		# Read column data from the file.
		while True:

			# Read line and break if no more lines exist in the file.
			p = f.tell()
			l = f.readline()
			if not l:
				break

			# Skip if a comment line with leading '#'.
			if (l.find('#') == 0):
				continue
			f.seek(p)

			# Read line and break if no more lines exist in the file.
			v = np.fromfile(f, count = n, sep = ' ')
			if (np.size(v) < n):
				break

			# Assign data to the appropriate column.
			for i in range(n):
				tb0.cols[i].ColumnData.append(v[i])
			tb0.RecordCount += 1
