#!/usr/bin/python

from fst2r2c_Shed_GeoPhysX import r2cfromfst_Shed_GeoPhysX, push_message

# To load rpnpy:
# . s.ssmuse.dot ENV/py/2.7/rpnpy/2.0.4

# Create normal drainage database if all FSTSHED_INFILE, FSTPHYS_INFILE, and R2CSHD_OUTFILE are defined using 'gru' approach.

push_message('\nTEST: Create normal drainage database if all FSTSHED_INFILE, FSTPHYS_INFILE, and R2CSHD_OUTFILE are defined using \'gru\' approach.')
r2cfromfst_Shed_GeoPhysX(
	FSTSHED_INFILE = 'shed.fst',
	FSTPHYS_INFILE = 'Gem_geophy.fst',
	R2CSHD_OUTFILE = 'test_dd_vfgru.r2c',
	R2CPRM_OUTFILE = 'test_pm.r2c',
	PHYSVF_MODE = 'gru',
	PHYSVF_ip1 = range(1199, (1174 - 1), -1),
	PHYSSOIL_ip1 = [ 1199, 1198, 1197, 1196, 1195, 1194, 1193 ]
)

# Create normal drainage database if all FSTSHED_INFILE, FSTPHYS_INFILE, and R2CSHD_OUTFILE are defined using 'frac' approach.

push_message('\nTEST: Create normal drainage database if all FSTSHED_INFILE, FSTPHYS_INFILE, and R2CSHD_OUTFILE are defined using \'frac\' approach.')
r2cfromfst_Shed_GeoPhysX(
	FSTSHED_INFILE = 'shed.fst',
	FSTPHYS_INFILE = 'Gem_geophy.fst',
	R2CSHD_OUTFILE = 'test_dd.r2c',
	R2CPRM_OUTFILE = 'test_pm_vffrac.r2c',
	PHYSVF_MODE = 'frac',
	PHYSVF_ip1 = range(1199, (1174 - 1), -1),
	PHYSSOIL_ip1 = [ 1199, 1198, 1197, 1196, 1195, 1194, 1193 ]
)

# Bad GeoPhysX options.

push_message('\nTEST: Bad GeoPhysX options.')
r2cfromfst_Shed_GeoPhysX(
	FSTSHED_INFILE = 'shed.fst',
	FSTPHYS_INFILE = 'Gem_geophy.fst',
	R2CSHD_OUTFILE = 'test_dd.r2c',
	R2CPRM_OUTFILE = 'test_pm_vffrac.r2c'
)

# Create limited drainage database for routing only if all FSTSHED_INFILE and R2CSHD_OUTFILE are defined.

push_message('\nTEST: Create limited drainage database for routing only if all FSTSHED_INFILE and R2CSHD_OUTFILE are defined.')
r2cfromfst_Shed_GeoPhysX(
	FSTSHED_INFILE = 'shed.fst',
	R2CSHD_OUTFILE = 'test_dd_shedfst_only.r2c'
)

# Create limited drainage database for land surface scheme only if all FSTPHYS_INFILE and R2CSHD_FILE are defined.

push_message('\nTEST: Create limited drainage database for land surface scheme only if all FSTPHYS_INFILE and R2CSHD_FILE are defined.')
r2cfromfst_Shed_GeoPhysX(
	FSTPHYS_INFILE = 'Gem_geophy.fst',
	R2CSHD_OUTFILE = 'test_dd_geophyfst_only.r2c',
	PHYSVF_MODE = 'frac'
)

# Create normal parameter file if all FSTSHED_INFILE, FSTPHYS_INFILE, and R2CPRM_OUTFILE are defined.

push_message('\nTEST: Create normal parameter file if all FSTSHED_INFILE, FSTPHYS_INFILE, and R2CPRM_OUTFILE are defined.')
r2cfromfst_Shed_GeoPhysX(
	FSTSHED_INFILE = 'shed.fst',
	FSTPHYS_INFILE = 'Gem_geophy.fst',
	R2CPRM_OUTFILE = 'test_pm_vffrac_noshedr2c.r2c',
	PHYSVF_MODE = 'frac',
	PHYSVF_ip1 = range(1199, (1174 - 1), -1),
	PHYSSOIL_ip1 = [ 1199, 1198, 1197, 1196, 1195, 1194, 1193 ]
)

# Create limited parameter file for routing only if all FSTSHED_INFILE and R2CPRM_OUTFILE are defined.

push_message('\nTEST: Create limited parameter file for routing only if all FSTSHED_INFILE and R2CPRM_OUTFILE are defined.')
r2cfromfst_Shed_GeoPhysX(
	FSTSHED_INFILE = 'shed.fst',
	R2CPRM_OUTFILE = 'test_pm_shedfst_only.r2c'
)

# Create limited parameter file for land surface scheme only if all FSTPHYS_INFILE and R2CPRM_OUTFILE are defined.

push_message('\nTEST: Create limited parameter file for land surface scheme only if all FSTPHYS_INFILE and R2CPRM_OUTFILE are defined.')
r2cfromfst_Shed_GeoPhysX(
	FSTPHYS_INFILE = 'Gem_geophy.fst',
	R2CPRM_OUTFILE = 'test_pm_geophyfst_only.r2c',
	PHYSVF_MODE = 'frac',
	PHYSVF_ip1 = range(1199, (1174 - 1), -1),
	PHYSSOIL_ip1 = [ 1199, 1198, 1197, 1196, 1195, 1194, 1193 ]
)
