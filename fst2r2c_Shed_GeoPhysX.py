#!/usr/bin/python

from os import path
from time import gmtime, strftime
import numpy as np
import rpnpy.librmn.all as rmn

# To load rpnpy:
# . s.ssmuse.dot ENV/py/2.7/rpnpy/2.0.4

# List to store warnings.

messages = []

def push_message(m):
	print(m)
	messages.append(m)

def push_error(m):
	print(m)
	exit()

# File names.

# Create normal drainage database if all FSTSHED_INFILE, FSTPHYS_INFILE, and R2CSHD_OUTFILE are defined.
# Create limited drainage database for routing only if all FSTSHED_INFILE and R2CSHD_OUTFILE are defined.
# Create limited drainage database for land surface scheme only if all FSTPHYS_INFILE and R2CSHD_FILE are defined.
# Create normal parameter file if all FSTSHED_INFILE, FSTPHYS_INFILE, and R2CPRM_OUTFILE are defined.
# Create limited parameter file for routing only if all FSTSHED_INFILE and R2CPRM_OUTFILE are defined.
# Create limited parameter file for land surface scheme only if all FSTPHYS_INFILE and R2CPRM_OUTFILE are defined.

FSTSHED_INFILE = 'shed.fst'
FSTPHYS_INFILE = 'Gem_geophy.fst'
R2CSHD_OUTFILE = 'test_dd.r2c'
R2CPRM_OUTFILE = 'test_pm.r2c'

# Stop if neither input file is defined.

if ((FSTSHED_INFILE == '') or (not path.exists(FSTSHED_INFILE))) and ((FSTPHYS_INFILE == '') or (not path.exists(FSTPHYS_INFILE))):
	push_error('ERROR: Neither shed nor physics input file is defined. The script cannot continue.')

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

	def loadattributefromfst(
		self, desrgrid, fstfid, fstnomvar, fstetiket = ' ', fstip1 = -1,
		intpopt = rmn.EZ_INTERP_NEAREST,
		constm = 1.0, constb = 0.0, constrmax = None, constrmin = None):

		# Grab the field.
		# Returns 'None' if no field is found.

		fstvar = rmn.fstlir(fstfid, nomvar = fstnomvar, etiket = fstetiket, ip1 = fstip1)
		if (fstvar is None):
			push_message('Unable to fetch field: %s. Attribute not appended.' % (fstnomvar))
			return
		self.AttributeData = fstvar['d']

		# Interpolate is mis-matched grid.
		# Only check two dimensions.
		# Coordinates are derived from the desired grid directly.

		newgrid = rmn.readGrid(fstfid, fstvar)
		if (newgrid['tag1'] != desrgrid['tag1']) or (newgrid['tag2'] != desrgrid['tag2']):
			desrll = rmn.gdll(desrgrid['id'])
			rmn.ezsetopt(rmn.EZ_OPT_INTERP_DEGREE, intpopt)
			self.AttributeData = rmn.gdllsval(newgrid['id'], desrll['lat'], desrll['lon'], fstvar['d'])

		# Apply transforms.

		if (not constrmax is None):
			self.AttributeData = max(self.AttributeData, constrmax)
		if (not constrmin is None):
			self.AttributeData = min(self.AttributeData, constrmin)
		self.AttributeData = constm*self.AttributeData + constb

class r2cfile(object):

	def __init__(self):
		self.meta = None
		self.grid = r2cgrid()
		self.attr = []

	def save(self, fpathr2cout):

		# Write the header.

		f = open(fpathr2cout, 'w')
		f.write('########################################\n')
		f.write(':FileType r2c ASCII EnSim 1.0\n')
		f.write('#\n')
		f.write('# DataType 2D Rect Cell\n')
		f.write('#\n')
		f.write(':Application fst2r2c_Shed.py\n')
		f.write(':Version 1.0\n')
		f.write(':WrittenBy fst2r2c_Shed.py\n')
		f.write(':CreationDate ' + strftime('%Y-%m-%d %H:%M:%S', gmtime()) + '\n')
		f.write('#\n')
		f.write('#---------------------------------------\n')
		f.write('#\n')
		if (not self.meta is None):
			f.write('#\n')
			f.write(':NominalGridSize_AL ' + str(self.meta.NominalGridSize_AL) + '\n')
			f.write(':ContourInterval ' + str(self.meta.ContourInterval) + '\n')
			f.write(':ImperviousArea ' + str(self.meta.ImperviousArea) + '\n')
			f.write(':ClassCount ' + str(self.meta.ClassCount) + '\n')
			f.write(':NumRiverClasses ' + str(self.meta.NumRiverClasses) + '\n')
			f.write(':ElevConversion ' + str(self.meta.ElevConversion) + '\n')
			f.write(':TotalNumOfGrids ' + str(self.meta.TotalNumOfGrids) + '\n')
			f.write(':NumGridsInBasin ' + str(self.meta.NumGridsInBasin) + '\n')
			f.write(':DebugGridNo ' + str(self.meta.DebugGridNo) + '\n')
		f.write('#\n')
		if (self.grid.Projection == 'LATLONG'):
			f.write(':Projection ' + self.grid.Projection + '\n')
			f.write(':Ellipsoid ' + self.grid.Ellipsoid + '\n')
		elif (self.grid.Projection == 'ROTLATLONG'):
			f.write(':Projection ' + self.grid.Projection + '\n')
			f.write(':CentreLatitude ' + str(self.grid.CentreLatitude) + '\n')
			f.write(':CentreLongitude ' + str(self.grid.CentreLongitude) + '\n')
			f.write(':RotationLatitude ' + str(self.grid.RotationLatitude) + '\n')
			f.write(':RotationLongitude ' + str(self.grid.RotationLongitude) + '\n')
			f.write(':Ellipsoid ' + self.grid.Ellipsoid + '\n')
		f.write('#\n')
		f.write(':xOrigin ' + str(self.grid.xOrigin) + '\n')
		f.write(':yOrigin ' + str(self.grid.yOrigin) + '\n')
		f.write('#\n')
		f.write('#\n')
		for i, a in enumerate(self.attr):
			if (not a.AttributeName is None):
				f.write(':AttributeName ' + str(i + 1) + ' ' + a.AttributeName + '\n')
			else:
				f.write(':AttributeName ' + str(i + 1) + ' Attribute' + str(i + 1) + '\n')
			if (not a.AttributeType is None):
				f.write(':AttributeType ' + str(i + 1) + ' ' + a.AttributeType + '\n')
			if (not a.AttributeUnits is None):
				f.write(':AttributeUnits ' + str(i + 1) + ' ' + a.AttributeUnits + '\n')
		f.write('#\n')
		f.write(':xCount ' + str(self.grid.xCount) + '\n')
		f.write(':yCount ' + str(self.grid.yCount) + '\n')
		f.write(':xDelta ' + str(self.grid.xDelta) + '\n')
		f.write(':yDelta ' + str(self.grid.yDelta) + '\n')
		f.write('#\n')
		f.write('#\n')
		f.write(':EndHeader\n')

		# Data.

		for i, a in enumerate(self.attr):
			if (not a.AttributeName is None):
				print('Saving ... ' + a.AttributeName)
			else:
				print('Saving ... Attribute ' + str(i + 1))
			np.savetxt(f, np.transpose(a.AttributeData), fmt = '%g')

		# Close file.

		f.close()

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
		push_error('The fst grid type ' + fstmatchgrid['grref'] + ' is not supported. The script cannot continue.')

def r2ccreateshed(fstmatchgrid, fpathr2cout, fshed = None, fphys = None):

	# Object to store r2c file.
	# The 'meta' section is required for the drainage database but not other r2c files.

	r2c = r2cfile()
	r2c.meta = r2cmeta()

	# Set the grid characteristics from the fst grid.

	r2cgridfromfst(fstmatchgrid, r2c)

	# Important notes on attributes:

	# Every attribute must have a name; if none is provided a generic one will be applied.
	# Default attribute units is none, in which case units can be omitted.
	# Default attribute type is float, in which case type can be omitted.
	# Attribute type integer should be explicitly provided and data converted to astype(int).

	# Append fields to the file.

	# Append WATROUTE controls and geophysical attributes.
	# Attributes are saved to variables as some are used in later calculations.

	if (not fshed is None):

		Rank = r2cattribute(AttributeName = 'Rank', AttributeType = 'integer')
		Rank.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'RANK')
		Rank.AttributeData = Rank.AttributeData.astype(int)
		r2c.attr.append(Rank)

		Next = r2cattribute(AttributeName = 'Next', AttributeType = 'integer')
		Next.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'NEXT')
		Next.AttributeData = Next.AttributeData.astype(int)
		r2c.attr.append(Next)

		DA = r2cattribute(AttributeName = 'DA', AttributeUnits = 'km**2')
		DA.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'DA')
		r2c.attr.append(DA)

		Bankfull = r2cattribute(AttributeName = 'Bankfull', AttributeUnits = 'm**3')
		Bankfull.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'BKFL')
		r2c.attr.append(Bankfull)

		ChnlSlope = r2cattribute(AttributeName = 'ChnlSlope', AttributeUnits = 'm m**-1')
		ChnlSlope.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'CSLP')
		r2c.attr.append(ChnlSlope)

		Elev = r2cattribute(AttributeName = 'Elev', AttributeUnits = 'm')
		Elev.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'ELEV')
		r2c.attr.append(Elev)

		ChnlLength = r2cattribute(AttributeName = 'ChnlLength', AttributeUnits = 'm')
		ChnlLength.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'CLEN')
		r2c.attr.append(ChnlLength)

		IAK = r2cattribute(AttributeName = 'IAK', AttributeType = 'integer', AttributeData = np.ones(np.shape(Rank.AttributeData), dtype=int))
		r2c.attr.append(IAK)

		Chnl = r2cattribute(AttributeName = 'Chnl', AttributeType = 'integer')
		Chnl.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'CHNL')
		Chnl.AttributeData = Chnl.AttributeData.astype(int)
		r2c.attr.append(Chnl)

		Reach = r2cattribute(AttributeName = 'Reach', AttributeType = 'integer')
		Reach.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'REAC')
		Reach.AttributeData = Reach.AttributeData.astype(int)
		r2c.attr.append(Reach)

		GridArea = r2cattribute(AttributeName = 'GridArea', AttributeUnits = 'm**2')
		GridArea.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'GRDA')
		r2c.attr.append(GridArea)

		VegLow = r2cattribute(AttributeName = 'VegLow', AttributeUnits = 'fraction')
		VegLow.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'VEGL')
		r2c.attr.append(VegLow)

		VegHigh = r2cattribute(AttributeName = 'VegHigh', AttributeUnits = 'fraction')
		VegHigh.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'VEGH')
		r2c.attr.append(VegHigh)

		# Important notes:

		# AL is the average side-length of the grid-cells (constant using UTM projection).
		# The land surface scheme does not operate on impervious areas; impervious area is considered when calculating average grid runoff.
		# Number of river classes is only used if parameters are assigned by IAK.
		# To recognize elevation in imperial units the units of the attribute must by 'ft' or 'feet'.
		# The number of grids in the basin are RANK > 0 where NEXT == 0.
		# Outlets are identified with NEXT == 0, and all outlets must be listed at the end of the stride of RANK
		#    (if two outlets exist in the basin, the last two RANK in the stride will have NEXT == 0).
		#    Typically, the number of grids in the basin < the total number of grids (but this is not always the case converting from fst).

		# Sanity checks.

		if (not np.any(GridArea.AttributeData[Next.AttributeData > 0] > 0.0)):
			push_message('WARNING: Cells exist in the basin where grid area is zero. This condition will nullify results and may trigger divide-by-zero traps in the land surface scheme.')
		if (not np.any(DA.AttributeData[Next.AttributeData > 0] > 0.0)):
			push_message('WARNING: Cells exist in the basin where drainage area is zero. This condition will trigger divide-by-zero traps in Watroute.')
		if (not np.any(ChnlSlope.AttributeData[Next.AttributeData > 0] > 0.0)):
			push_message('WARNING: Cells exist in the basin where channel slope is zero. This condition will nullify results in Watroute.')
		if (not np.any(ChnlLength.AttributeData[Next.AttributeData > 0] > 0.0)):
			push_message('WARNING: Cells exist in the basin where channel length is zero. This condition will nullify results in Watroute.')
		if (not np.any(Next.AttributeData[Rank.AttributeData > 0] == 0)):
			push_message('WARNING: No outlets exist in the basin. Outlets are ranked cells where Next is zero. This condition is undesirable, but will not crash Watroute.')
		if (not np.count_nonzero(np.unique(Rank.AttributeData)) == np.amax(Rank.AttributeData)):
			push_message('WARNING: The succession of ranked cells is not continuous. This condition will not crash Watroute, but may result in lost water.')

		# Update meta-information.

		r2c.meta.NominalGridSize_AL = np.sqrt(np.average(GridArea.AttributeData, weights = (GridArea.AttributeData > 0)))
		r2c.meta.ContourInterval = 1.0
		r2c.meta.ImperviousArea = 0
		r2c.meta.NumRiverClasses = np.count_nonzero(np.unique(IAK.AttributeData))
		if (not Elev.AttributeUnits is None) and ((Elev.AttributeUnits.lower() == 'ft') or (Elev.AttributeUnits.lower() == 'feet')):
			r2c.meta.ElevConversion = 0.305
		else:
			r2c.meta.ElevConversion = 1.0
		r2c.meta.TotalNumOfGrids = np.count_nonzero(Rank.AttributeData)
		r2c.meta.NumGridsInBasin = np.count_nonzero(Next.AttributeData)
		r2c.meta.DebugGridNo = np.amax(Rank.AttributeData[Next.AttributeData > 0])

	# If grid type is 'E', write latitude and longitude fields.

	if (fstmatchgrid['grref'] == 'E'):

		lalo = rmn.gdll(fstmatchgrid['id'])

		LA = r2cattribute(AttributeName = 'Latitude', AttributeUnits = 'degrees', AttributeData = lalo['lat'])
		r2c.attr.append(LA)

		LO = r2cattribute(AttributeName = 'Longitude', AttributeUnits = 'degrees', AttributeData = lalo['lon'])
		r2c.attr.append(LO)

	# Append land cover attributes.

	if (not fphys is None):

		IntSlope = r2cattribute(AttributeName = 'IntSlope', AttributeUnits = 'm m**-1')
		IntSlope.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fphys, fstnomvar = 'SLOP')
		r2c.attr.append(IntSlope)

		# Fetch all 26 cover types from GemPhysX, which span ip1 1199->1174.
		# Special covers: glaciers, wetlands, water, impervious.
		# Separate keywords in case smart filtering is added in a future version of MESH.

		SumClass = np.zeros(np.shape(IntSlope.AttributeData))
		r2c.meta.ClassCount = 0
		for ip1 in range(1199, (1174 - 1), -1):
			a = r2cattribute(
				AttributeUnits = 'fraction'
			)
			if (ip1 == 1199):
				a.AttributeName = '\"' + str(ip1) + ' sea water"'
			elif (ip1 == 1198):
				a.AttributeName = '\"' + str(ip1) + ' glaciers\"'
			elif (ip1 == 1197):
				a.AttributeName = '\"' + str(ip1) + ' inland lake water\"'
			elif (ip1 == 1196):
				a.AttributeName = '\"' + str(ip1) + ' evergreen needleleaf trees\"'
			elif (ip1 == 1195):
				a.AttributeName = '\"' + str(ip1) + ' evergreen broadleaf trees\"'
			elif (ip1 == 1194):
				a.AttributeName = '\"' + str(ip1) + ' deciduous needleleaf trees\"'
			elif (ip1 == 1193):
				a.AttributeName = '\"' + str(ip1) + ' deciduous broadleaf trees\"'
			elif (ip1 == 1192):
				a.AttributeName = '\"' + str(ip1) + ' tropical broadleaf trees\"'
			elif (ip1 == 1191):
				a.AttributeName = '\"' + str(ip1) + ' drought deciduous trees\"'
			elif (ip1 == 1190):
				a.AttributeName = '\"' + str(ip1) + ' evergreen broadleaf shrubs\"'
			elif (ip1 == 1189):
				a.AttributeName = '\"' + str(ip1) + ' deciduous shrubs\"'
			elif (ip1 == 1188):
				a.AttributeName = '\"' + str(ip1) + ' thorn shrubs\"'
			elif (ip1 == 1187):
				a.AttributeName = '\"' + str(ip1) + ' short grass and forbs\"'
			elif (ip1 == 1186):
				a.AttributeName = '\"' + str(ip1) + ' long grass\"'
			elif (ip1 == 1185):
				a.AttributeName = '\"' + str(ip1) + ' crops\"'
			elif (ip1 == 1184):
				a.AttributeName = '\"' + str(ip1) + ' rice\"'
			elif (ip1 == 1183):
				a.AttributeName = '\"' + str(ip1) + ' sugar\"'
			elif (ip1 == 1182):
				a.AttributeName = '\"' + str(ip1) + ' maize\"'
			elif (ip1 == 1181):
				a.AttributeName = '\"' + str(ip1) + ' cotton\"'
			elif (ip1 == 1180):
				a.AttributeName = '\"' + str(ip1) + ' irrigated crops\"'
			elif (ip1 == 1179):
				a.AttributeName = '\"' + str(ip1) + ' urban\"'
			elif (ip1 == 1178):
				a.AttributeName = '\"' + str(ip1) + ' tundra\"'
			elif (ip1 == 1177):
				a.AttributeName = '\"' + str(ip1) + ' swamp wetlands\"'
			elif (ip1 == 1176):
				a.AttributeName = '\"' + str(ip1) + ' desert\"'
			elif (ip1 == 1175):
				a.AttributeName = '\"' + str(ip1) + ' mixed wood forest trees\"'
			elif (ip1 == 1174):
				a.AttributeName = '\"' + str(ip1) + ' mixed shrubs\"'
			a.loadattributefromfst(
				desrgrid = fstmatchgrid,
				fstfid = fphys,
				fstnomvar = 'VF',
				fstip1 = ip1
			)
			r2c.attr.append(a)
			SumClass += a.AttributeData
			r2c.meta.ClassCount += 1

		# Append dummy land cover class for impervious areas (legacy requirement).

		a = r2cattribute(AttributeName = 'impervious', AttributeUnits = 'fraction', AttributeData = np.zeros(np.shape(IntSlope.AttributeData)))
		r2c.attr.append(a)
		r2c.meta.ClassCount += 1

		# Sanity checks.

	# Write output.

	r2c.save(fpathr2cout)

def r2ccreateparam(fstmatchgrid, fpathr2cout, fshed = None, fphys = None):

	# Object to store r2c file.
	# The 'meta' section is not required for parameter files.

	r2c = r2cfile()

	# Set the grid characteristics from the fst grid.

	r2cgridfromfst(fstmatchgrid, r2c)

	# Important notes on attributes:

	# Every attribute must have a name; if none is provided a generic one will be applied.
	# Default attribute units is none, in which case units can be omitted.
	# Default attribute type is float, in which case type can be omitted.
	# Attribute type integer should be explicitly provided and data converted to astype(int).

	# Append fields to the file.

	if (not fshed is None):

		a = r2cattribute(AttributeName = 'R2N')
		a.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'R2N', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'R1N')
		a.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'R1N', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'MNDR')
		a.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'MNDR', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'WIDEP')
		a.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'WIDP', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'AA2')
		a.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'AA2', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'AA3')
		a.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'AA3', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'AA4')
		a.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'AA4', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'PWR')
		a.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'PWR', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'FLZ')
		a.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fshed, fstnomvar = 'FLZ', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

	if (not fphys is None):

		a = r2cattribute(AttributeName = 'LNZ0', AttributeUnits = 'ln(m)')
		a.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fphys, fstnomvar = 'ZP')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'DDEN', AttributeUnits = 'km km**-2')
		a.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fphys, fstnomvar = 'DRND', constm = 1000.0)
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'XSLP', AttributeUnits = 'm m**-1')
		a.loadattributefromfst(desrgrid = fstmatchgrid, fstfid = fphys, fstnomvar = 'SLOP')
		r2c.attr.append(a)

		# Fetch soil texture for 7 soil layers, which span ip1 1199->1193.
		# MESH-SVS presently requires 7 soil layers.

                i = 1
		for ip1 in range(1199, (1193 - 1), -1):
			a = r2cattribute(
				AttributeName = 'SAND ' + str(i),
				AttributeUnits = '%'
			)
			a.loadattributefromfst(
				desrgrid = fstmatchgrid,
				fstfid = fphys,
				fstnomvar = 'J1',
				fstip1 = ip1
			)
			r2c.attr.append(a)
			i += 1

		i = 1
		for ip1 in range(1199, (1193 - 1), -1):
			a = r2cattribute(
				AttributeName = 'CLAY ' + str(i),
				AttributeUnits = '%'
			)
			a.loadattributefromfst(
				desrgrid = fstmatchgrid,
				fstfid = fphys,
				fstnomvar = 'J2',
				fstip1 = ip1
			)
			r2c.attr.append(a)
			i += 1

	# Write output.

	r2c.save(fpathr2cout)

# Open fst files.

if (path.exists(FSTSHED_INFILE)):
	fshed = rmn.fstopenall(FSTSHED_INFILE)
	rec = rmn.fstlir(fshed, etiket = 'GRID')
	if (rec is None):
		push_error('Records do not exist in ' + FSTSHED_INFILE + ' of etiket GRID. The script cannot continue.')
	fshedgrid = rmn.readGrid(fshed, rec)
	if (not 'dlat' in fshedgrid) or (not 'dlon' in fshedgrid):
		push_error('The grid of ' + FSTSHED_INFILE + ' must contain the dlat and dlon fields. The script cannot continue.')
else:
	fshed = None
if (path.exists(FSTPHYS_INFILE)):
	fphys = rmn.fstopenall(FSTPHYS_INFILE)
	rec = rmn.fstlir(fphys, etiket = 'GENPHYSX')
	if (rec is None):
		push_error('Records do not exist in ' + FSTPHYS_INFILE + ' of etiket GENPHYSX. The script cannot continue.')
	fphysgrid = rmn.readGrid(fphys, rec)
	if (not 'dlat' in fphysgrid) or (not 'dlon' in fphysgrid):
		push_error('The grid of ' + FSTPHYS_INFILE + ' must contain the dlat and dlon fields. The script cannot continue.')
else:
	fphys = None

# Define the grid project.
# Use the grid with the smallest delta.

fstmatchgrid = None
if (not fshed is None) and (fphys is None):
	fstmatchgrid = fshedgrid
elif (fshed is None) and (not fphys is None):
	fstmatchgrid = fphysgrid
elif (fshedgrid['dlat'] <= fphysgrid['dlat']) or (fshedgrid['dlon'] <= fphysgrid['dlon']):
	fstmatchgrid = fshedgrid
else:
	fstmatchgrid = fphysgrid
if (fstmatchgrid is None):
	push_error('No grid is defined. The script cannot continue.')

# Create drainage database.

if (R2CSHD_OUTFILE != ''):
	r2ccreateshed(fstmatchgrid = fstmatchgrid, fpathr2cout = R2CSHD_OUTFILE, fshed = fshed, fphys = fphys)

# Create parameter file.

if (R2CPRM_OUTFILE != ''):
	r2ccreateparam(fstmatchgrid = fstmatchgrid, fpathr2cout = R2CPRM_OUTFILE, fshed = fshed, fphys = fphys)

# Close fst files.

if (not fshed is None):
	rmn.fstcloseall(fshed)
if (not fphys is None):
	rmn.fstcloseall(fphys)

# Recap messages.

print('Recapping all messages ...')
for m in messages:
	print(m)

