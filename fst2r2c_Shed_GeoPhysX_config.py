#!/usr/bin/python

from fst2r2c_Shed_GeoPhysX import r2cfromfst_Shed_GeoPhysX

# To load rpnpy:
# . s.ssmuse.dot ENV/py/2.7/rpnpy/2.0.4

# File names.

# Create normal drainage database if all FSTSHED_INFILE, FSTPHYS_INFILE, and R2CSHD_OUTFILE are defined.
# Create limited drainage database for routing only if all FSTSHED_INFILE and R2CSHD_OUTFILE are defined.
# Create limited drainage database for land surface scheme only if all FSTPHYS_INFILE and R2CSHD_FILE are defined.
# Create normal parameter file if all FSTSHED_INFILE, FSTPHYS_INFILE, and R2CPRM_OUTFILE are defined.
# Create limited parameter file for routing only if all FSTSHED_INFILE and R2CPRM_OUTFILE are defined.
# Create limited parameter file for land surface scheme only if all FSTPHYS_INFILE and R2CPRM_OUTFILE are defined.

FSTSHED_INFILE = 'shed.fst'
FSTPHYS_INFILE = 'Gem_geophy.fst'
R2CSHD_OUTFILE = 'MESH_drainage_database.r2c'
R2CPRM_OUTFILE = 'MESH_parameters.r2c'

# Options.

# PHYSVF_MODE:
#	= 'frac' add as parameter in R2CPRM_OUTFILE, MESH-SVS emulates GEM-Hydro 1 GRU per grid.
#	= 'gru' add as GRUs in R2CSHD_OUTFILE, MESH runs in tile mode (e.g., MESH-CLASS).

PHYSVF_MODE = 'gru'
PHYSVF_MODE = 'frac'

# PHYSVF_ip1:
#	= range(1199, (11974 - 1), -1) will iterate from 1199->1174.
#	= [ 1199, 1198 ] will iterate the defined subset.

PHYSVF_ip1 = range(1199, (1174 - 1), -1)

# PHYSSOIL_ip1:
#	= range(1199, (1192 - 1), -1) will iterate from 1199->1192.
#	= [ 1199, 1198 ] will iterate the defined subset.

PHYSSOIL_ip1 = range(1199, (1192 - 1), -1)
# MESH-SVS presently requires 7 soil layers.
PHYSSOIL_ip1 = [ 1199, 1198, 1197, 1196, 1195, 1194, 1193 ]

# Process files.

r2cfromfst_Shed_GeoPhysX(FSTSHED_INFILE, FSTPHYS_INFILE, R2CSHD_OUTFILE, R2CPRM_OUTFILE, PHYSVF_MODE, PHYSVF_ip1, PHYSSOIL_ip1)
