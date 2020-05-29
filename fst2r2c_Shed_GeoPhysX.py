#!/usr/bin/python

from os import path
from time import gmtime, strftime
import numpy as np
import rpnpy.librmn.all as rmn
from ensim_utils import *

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

# r2c structures, core fst-related routines imported from ensim_utils.

def r2cfromgemphyvf(fstmatchgrid, fstfid, r2c, PHYSVF_ip1):

	# Fetch land covers from GemPhysX.
	# Special covers: glaciers, wetlands, water, impervious.
	# Separate keywords in case smart filtering is added in a future version of MESH.

	SumClass = np.zeros((r2c.grid.xCount, r2c.grid.yCount))
	if (not r2c.meta is None):
		r2c.meta.ClassCount = 0
	for ip1 in PHYSVF_ip1:
		a = r2cattribute(AttributeUnits = 'fraction')
		if (ip1 == 1199):
			a.AttributeName = 'sea water'
		elif (ip1 == 1198):
			a.AttributeName = 'glaciers'
		elif (ip1 == 1197):
			a.AttributeName = 'inland lake water'
		elif (ip1 == 1196):
			a.AttributeName = 'evergreen needleleaf trees'
		elif (ip1 == 1195):
			a.AttributeName = 'evergreen broadleaf trees'
		elif (ip1 == 1194):
			a.AttributeName = 'deciduous needleleaf trees'
		elif (ip1 == 1193):
			a.AttributeName = 'deciduous broadleaf trees'
		elif (ip1 == 1192):
			a.AttributeName = 'tropical broadleaf trees'
		elif (ip1 == 1191):
			a.AttributeName = 'drought deciduous trees'
		elif (ip1 == 1190):
			a.AttributeName = 'evergreen broadleaf shrubs'
		elif (ip1 == 1189):
			a.AttributeName = 'deciduous shrubs'
		elif (ip1 == 1188):
			a.AttributeName = 'thorn shrubs'
		elif (ip1 == 1187):
			a.AttributeName = 'short grass and forbs'
		elif (ip1 == 1186):
			a.AttributeName = 'long grass'
		elif (ip1 == 1185):
			a.AttributeName = 'crops'
		elif (ip1 == 1184):
			a.AttributeName = 'rice'
		elif (ip1 == 1183):
			a.AttributeName = 'sugar'
		elif (ip1 == 1182):
			a.AttributeName = 'maize'
		elif (ip1 == 1181):
			a.AttributeName = 'cotton'
		elif (ip1 == 1180):
			a.AttributeName = 'irrigated crops'
		elif (ip1 == 1179):
			a.AttributeName = 'urban'
		elif (ip1 == 1178):
			a.AttributeName = 'tundra'
		elif (ip1 == 1177):
			a.AttributeName = 'swamp wetlands'
		elif (ip1 == 1176):
			a.AttributeName = 'desert'
		elif (ip1 == 1175):
			a.AttributeName = 'mixed wood forest trees'
		elif (ip1 == 1174):
			a.AttributeName = 'mixed shrubs'
		a.AttributeName = ('\"VF %d ' % ip1) + a.AttributeName + '\"'
		r2cattributefromfst(a, fstmatchgrid, fstfid, fstnomvar = 'VF', fstip1 = ip1)
		r2c.attr.append(a)
		SumClass += a.AttributeData
		if (not r2c.meta is None):
			r2c.meta.ClassCount += 1
	if (not np.all(SumClass > 0.0)):
		push_message('WARNING: Cells exist in the basin where the total fraction of land cover is zero.')

def r2cfromgemphysoil(fstmatchgrid, fstfid, r2c, PHYSSOIL_ip1):

	# Fetch soil texture for soil layers.

        i = 1
	for ip1 in PHYSSOIL_ip1:
		a = r2cattribute(AttributeName = ('\"SAND %d\"' % i), AttributeUnits = '%')
		r2cattributefromfst(a, fstmatchgrid, fstfid, fstnomvar = 'J1', fstip1 = ip1)
		r2c.attr.append(a)
		i += 1

	i = 1
	for ip1 in PHYSSOIL_ip1:
		a = r2cattribute(AttributeName = ('\"CLAY %d\"' % i), AttributeUnits = '%')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fstfid, fstnomvar = 'J2', fstip1 = ip1)
		r2c.attr.append(a)
		i += 1

def r2ccreateshed(fstmatchgrid, fpathr2cout, fshed = None, fphys = None, PHYSVF_MODE = '', PHYSVF_ip1 = []):

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
	# Some attributes are saved to variables to be used in sanity checks or in calculating other attributes.

	if (not fshed is None):

		# Important notes:

		# AL is the average side-length of the grid-cells (constant using UTM projection).
		# The land surface scheme does not operate on impervious areas; impervious area is considered when calculating average grid runoff.
		# Number of river classes is only used if parameters are assigned by IAK.
		# To recognize elevation in imperial units the units of the attribute must by 'ft' or 'feet'.
		# The number of grids in the basin are RANK > 0 where NEXT == 0.
		# Outlets are identified with NEXT == 0, and all outlets must be listed at the end of the stride of RANK
		#    (if two outlets exist in the basin, the last two RANK in the stride will have NEXT == 0).
		#    Typically, the number of grids in the basin < the total number of grids (but this is not always the case converting from fst).

		Rank = r2cattribute(AttributeName = 'Rank', AttributeType = 'integer')
		r2cattributefromfst(Rank, fstmatchgrid, fstfid = fshed, fstnomvar = 'RANK')
		r2c.attr.append(Rank)
		if (not np.count_nonzero(np.unique(Rank.AttributeData)) == np.amax(Rank.AttributeData)):
			push_message('WARNING: The succession of ranked cells is not continuous. This condition will not crash Watroute, but may result in lost water.')

		Next = r2cattribute(AttributeName = 'Next', AttributeType = 'integer')
		r2cattributefromfst(Next, fstmatchgrid, fstfid = fshed, fstnomvar = 'NEXT')
		r2c.attr.append(Next)
		if (not np.any(Next.AttributeData[Rank.AttributeData > 0] == 0)):
			push_message('WARNING: No outlets exist in the basin. Outlets are cells with Rank where Next is zero. This condition is undesirable, but will not crash Watroute.')

		a = r2cattribute(AttributeName = 'DA', AttributeUnits = 'km**2')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'DA')
		r2c.attr.append(a)
		if (not np.any(a.AttributeData[Next.AttributeData > 0] > 0.0)):
			push_message('WARNING: Cells exist in the basin where drainage area is zero. This condition will trigger divide-by-zero traps in Watroute.')

		a = r2cattribute(AttributeName = 'Bankfull', AttributeUnits = 'm**3')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'BKFL')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'ChnlSlope', AttributeUnits = 'm m**-1')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'CSLP')
		r2c.attr.append(a)
		if (not np.any(a.AttributeData[Next.AttributeData > 0] > 0.0)):
			push_message('WARNING: Cells exist in the basin where channel slope is zero. This condition may cause undesirable results in Watroute.')

		Elev = r2cattribute(AttributeName = 'Elev', AttributeUnits = 'm')
		r2cattributefromfst(Elev, fstmatchgrid, fstfid = fshed, fstnomvar = 'ELEV')
		r2c.attr.append(Elev)

		a = r2cattribute(AttributeName = 'ChnlLength', AttributeUnits = 'm')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'CLEN')
		r2c.attr.append(a)
		if (not np.any(a.AttributeData[Next.AttributeData > 0] > 0.0)):
			push_message('WARNING: Cells exist in the basin where channel length is zero. This condition may cause undesirable results in Watroute.')

		IAK = r2cattribute(AttributeName = 'IAK', AttributeType = 'integer', AttributeData = np.ones((r2c.grid.xCount, r2c.grid.yCount), dtype = int))
		r2c.attr.append(IAK)

		a = r2cattribute(AttributeName = 'Chnl', AttributeType = 'integer')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'CHNL')
		a.AttributeData = a.AttributeData.astype(int)
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'Reach', AttributeType = 'integer')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'REAC')
		a.AttributeData = a.AttributeData.astype(int)
		r2c.attr.append(a)

		GridArea = r2cattribute(AttributeName = 'GridArea', AttributeUnits = 'm**2')
		r2cattributefromfst(GridArea, fstmatchgrid, fstfid = fshed, fstnomvar = 'GRDA')
		r2c.attr.append(GridArea)
		if (not np.any(GridArea.AttributeData[Next.AttributeData > 0] > 0.0)):
			push_message('WARNING: Cells exist in the basin where grid area is zero. This condition will nullify results and may trigger divide-by-zero traps in the land surface scheme.')

		a = r2cattribute(AttributeName = 'VegLow', AttributeUnits = 'fraction')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'VEGL')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'VegHigh', AttributeUnits = 'fraction')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'VEGH')
		r2c.attr.append(a)

	else:

		# Append dummy fields (when shed.fst is not used).

		Rank = r2cattribute(AttributeName = 'Rank', AttributeType = 'integer')
		Rank.AttributeData = np.zeros((r2c.grid.xCount, r2c.grid.yCount), dtype = int)
		i = 1
		for y in range(r2c.grid.yCount):
			for x in range(r2c.grid.xCount):
				Rank.AttributeData[x, y] = i
				i += 1
		r2c.attr.append(Rank)
		push_message('REMARK: Shed is not defined. A dummy Rank will be appended to the file.')

		Next = r2cattribute(AttributeName = 'Next', AttributeType = 'integer')
		Next.AttributeData = np.zeros((r2c.grid.xCount, r2c.grid.yCount), dtype = int)
		i = 2
		for y in range(r2c.grid.yCount):
			for x in range(r2c.grid.xCount):
				Next.AttributeData[x, y] = i
				i += 1
		r2c.attr.append(Next)
		push_message('REMARK: Shed is not defined. A dummy Next will be appended to the file.')

		Elev = r2cattribute(AttributeName = 'Elev', AttributeUnits = 'm', AttributeData = np.zeros((r2c.grid.xCount, r2c.grid.yCount)))
		r2c.attr.append(Elev)
		push_message('REMARK: Shed is not defined. A dummy Elev will be appended to the file.')

		IAK = r2cattribute(AttributeName = 'IAK', AttributeType = 'integer', AttributeData = np.zeros((r2c.grid.xCount, r2c.grid.yCount), dtype = int))
		r2c.attr.append(IAK)
		push_message('REMARK: Shed is not defined. A dummy IAK will be appended to the file.')

		GridArea = r2cattribute(AttributeName = 'GridArea', AttributeUnits = 'm**2', AttributeData = np.ones((r2c.grid.xCount, r2c.grid.yCount)))
		r2c.attr.append(GridArea)
		push_message('REMARK: Shed is not defined. A dummy GridArea field will be appended to the file.')

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

		a = r2cattribute(AttributeName = 'Latitude', AttributeUnits = 'degrees', AttributeData = lalo['lat'])
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'Longitude', AttributeUnits = 'degrees', AttributeData = lalo['lon'])
		r2c.attr.append(a)

	# Append land cover attributes from geophys.fst.

	if (not fphys is None):

		a = r2cattribute(AttributeName = 'IntSlope', AttributeUnits = 'm m**-1')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fphys, fstnomvar = 'SLOP')
		r2c.attr.append(a)

		# PHYSVF_MODE = 'gru'

		if (PHYSVF_MODE == 'gru'):
			r2cfromgemphyvf(fstmatchgrid, fphys, r2c, PHYSVF_ip1)

		# PHYSVF_MODE = 'frac'

		elif (PHYSVF_MODE == 'frac'):
			a = r2cattribute(AttributeName = '\"land cover\"', AttributeUnits = 'fraction', AttributeData = np.ones((r2c.grid.xCount, r2c.grid.yCount)))
			r2c.attr.append(a)
			r2c.meta.ClassCount += 1
			push_message('REMARK: PHYSVF_MODE frac is active. GeoPhysX land cover will be appended to the parameter file.')

		# PHYSVF_MODE (unknown)

		else:
			push_message('WARNING: GeoPhysX file is active but no land covers exist or PHYSVF_MODE is not known or ip1 levels have not been defined. This may cause undesirable results when running the model.')

	else:

		# Append dummy land cover attribute (when geophys.fst is not used).

		a = r2cattribute(AttributeName = '\"land cover\"', AttributeUnits = 'fraction', AttributeData = np.ones((r2c.grid.xCount, r2c.grid.yCount)))
		r2c.attr.append(a)
		r2c.meta.ClassCount += 1
		push_message('REMARK: GeoPhysX is not defined or PHYSVF_MODE gru is active. A dummy land cover will be appended to the parameter file.')

	# Append dummy land cover class for impervious areas (legacy requirement).

	a = r2cattribute(AttributeName = 'impervious', AttributeUnits = 'fraction', AttributeData = np.zeros((r2c.grid.xCount, r2c.grid.yCount)))
	r2c.attr.append(a)
	r2c.meta.ClassCount += 1

	# Write output.

	r2cfilecreateheader(r2c, fpathr2cout)
	r2cfileappendattributes(r2c, fpathr2cout)

def r2ccreateparam(fstmatchgrid, fpathr2cout, fshed = None, fphys = None, PHYSVF_MODE = '', PHYSVF_ip1 = [], PHYSSOIL_ip1 = []):

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

		# Next is used in sanity checks not saved to the parameter file.

		Next = r2cattribute()
		r2cattributefromfst(Next, fstmatchgrid, fstfid = fshed, fstnomvar = 'NEXT')

		# Watroute channel routing parameters.

		a = r2cattribute(AttributeName = 'R2N')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'R2N', fstetiket = 'CONSTANT')
		r2c.attr.append(a)
		if (not np.any(a.AttributeData[Next.AttributeData > 0] > 0.0)):
			push_message('WARNING: Cells exist in the basin where R2N is not assigned. This condition may cause undesirable results in Watroute.')

		a = r2cattribute(AttributeName = 'R1N')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'R1N', fstetiket = 'CONSTANT')
		r2c.attr.append(a)
		if (not np.any(a.AttributeData[Next.AttributeData > 0] > 0.0)):
			push_message('WARNING: Cells exist in the basin where R1N is not assigned. This condition may cause undesirable results in Watroute.')

		a = r2cattribute(AttributeName = 'MNDR')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'MNDR', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'WIDEP')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'WIDP', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'AA2')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'AA2', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'AA3')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'AA3', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'AA4')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'AA4', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		# Baseflow parameters.

		a = r2cattribute(AttributeName = 'PWR')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'PWR', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

		a = r2cattribute(AttributeName = 'FLZ')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fshed, fstnomvar = 'FLZ', fstetiket = 'CONSTANT')
		r2c.attr.append(a)

	if (not fphys is None):

		# PHYSVF_MODE = 'frac'

		if (PHYSVF_MODE == 'frac'):
			r2cfromgemphyvf(fstmatchgrid, fphys, r2c, PHYSVF_ip1)

		# Canopy parameters.

		a = r2cattribute(AttributeName = 'LNZ0', AttributeUnits = 'ln(m)')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fphys, fstnomvar = 'ZP')
		r2c.attr.append(a)

		# Interflow parameters.

		a = r2cattribute(AttributeName = 'DDEN', AttributeUnits = 'km km**-2')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fphys, fstnomvar = 'DRND', constmul = 1000.0)
		r2c.attr.append(a)
		if (not np.all(a > 0.0)):
			push_message('WARNING: Cells exist in the basin where drainage density is zero. This condition may trigger bad math traps in WATROF/WATDRN.')

		a = r2cattribute(AttributeName = 'XSLP', AttributeUnits = 'm m**-1')
		r2cattributefromfst(a, fstmatchgrid, fstfid = fphys, fstnomvar = 'SLOP')
		r2c.attr.append(a)
		if (not np.all(a > 0.0)):
			push_message('WARNING: Cells exist in the basin where soil slope is zero. This condition may trigger bad math traps in WATROF/WATDRN.')

		# Fetch soil texture for soil layers.

		r2cfromgemphysoil(fstmatchgrid, fphys, r2c, PHYSSOIL_ip1)

	# Write output.

	r2cfilecreateheader(r2c, fpathr2cout)
	r2cfileappendattributes(r2c, fpathr2cout)

def r2cfromfst_Shed_GeoPhysX(

	# File names.

	FSTSHED_INFILE = '',
	FSTPHYS_INFILE = '',
	R2CSHD_OUTFILE = '',
	R2CPRM_OUTFILE = '',

	# Options.

	PHYSVF_MODE = '',
	PHYSVF_ip1 = [],
	PHYSSOIL_ip1 = []

	):

	# Stop if neither input file is defined.

	if ((FSTSHED_INFILE == '') or (not path.exists(FSTSHED_INFILE))) and ((FSTPHYS_INFILE == '') or (not path.exists(FSTPHYS_INFILE))):
		push_error('ERROR: Neither shed nor physics input file is defined. The script cannot continue.')

	# Summarize inputs.

	push_message('INFO: Processing files with the following conditions...')
	if (not FSTSHED_INFILE == ''):
		push_message('  FSTSHED_INFILE = ' + FSTSHED_INFILE)
	else:
		push_message('  FSTSHED_INFILE = (not active)')
	if (not FSTPHYS_INFILE == ''):
		push_message('  FSTPHYS_INFILE = ' + FSTPHYS_INFILE)
	else:
		push_message('  FSTPHYS_INFILE = (not active)')
	if (not R2CSHD_OUTFILE == ''):
		push_message('  R2CSHD_OUTFILE = ' + R2CSHD_OUTFILE)
	else:
		push_message('  R2CSHD_OUTFILE = (not active)')
	if (not R2CPRM_OUTFILE == ''):
		push_message('  R2CPRM_OUTFILE = ' + R2CPRM_OUTFILE)
	else:
		push_message('  R2CPRM_OUTFILE = (not active)')
	if (not PHYSVF_MODE == ''):
		push_message('  PHYSVF_MODE = ' + PHYSVF_MODE)
	else:
		push_message('  PHYSVF_MODE = (not active)')
	if (PHYSVF_ip1):
		push_message('  PHYSVF_ip1 = [ ' + ', '.join([str(i) for i in PHYSVF_ip1]) + ' ]')
	else:
		push_message('  PHYSVF_ip1 = (not active)')
	if (PHYSSOIL_ip1):
		push_message('  PHYSSOIL_ip1 = [ ' + ', '.join([str(i) for i in PHYSSOIL_ip1]) + ' ]')
	else:
		push_message('  PHYSSOIL_ip1 = (not active)')

	# Open fst files.

	if (path.exists(FSTSHED_INFILE)):
		fshed = rmn.fstopenall(FSTSHED_INFILE)
		rec = rmn.fstlir(fshed, etiket = 'CONSTANT')
		if (rec is None):
			push_error('Records do not exist in ' + FSTSHED_INFILE + ' of etiket CONSTANT. The script cannot continue.')
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
		push_message('INFO: Matching domain to ' + FSTSHED_INFILE + ' specification.')
		fstmatchgrid = fshedgrid
	elif (fshed is None) and (not fphys is None):
		push_message('INFO: Matching domain to ' + FSTPHYS_INFILE + ' specification.')
		fstmatchgrid = fphysgrid
	elif (fshedgrid['dlat'] <= fphysgrid['dlat']) or (fshedgrid['dlon'] <= fphysgrid['dlon']):
		push_message('INFO: Matching domain to ' + FSTSHED_INFILE + ' specification.')
		fstmatchgrid = fshedgrid
	else:
		push_message('INFO: Matching domain to ' + FSTPHYS_INFILE + ' specification.')
		fstmatchgrid = fphysgrid
	if (fstmatchgrid is None):
		push_error('No grid is defined. The script cannot continue.')

	# Create drainage database.

	if (R2CSHD_OUTFILE != ''):
		r2ccreateshed(fstmatchgrid, fpathr2cout = R2CSHD_OUTFILE, fshed = fshed, fphys = fphys, PHYSVF_MODE = PHYSVF_MODE, PHYSVF_ip1 = PHYSVF_ip1)

	# Create parameter file.

	if (R2CPRM_OUTFILE != ''):
		r2ccreateparam(fstmatchgrid, fpathr2cout = R2CPRM_OUTFILE, fshed = fshed, fphys = fphys, PHYSVF_MODE = PHYSVF_MODE, PHYSVF_ip1 = PHYSVF_ip1, PHYSSOIL_ip1 = PHYSSOIL_ip1)

	# Close fst files.

	if (not fshed is None):
		rmn.fstcloseall(fshed)
	if (not fphys is None):
		rmn.fstcloseall(fphys)

	# Recap messages.

	print('Recapping all messages ...')
	for m in messages:
		print(m)
	print('Processing has completed.')
