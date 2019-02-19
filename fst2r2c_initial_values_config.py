#!/usr/bin/python

from fst2r2c_initial_values import r2cfromfst_initial_values

# To load rpnpy:
# . s.ssmuse.dot ENV/py/2.7/rpnpy/2.0.4

# File names.

# Create initial values file if all FST_INFILE and R2C_OUTFILE are defined.

FST_INFILE = 'flow_init.fst'
R2C_OUTFILE = 'MESH_initial_values.r2c'

# Options.

# Process files.

r2cfromfst_initial_values(FST_INFILE, R2C_OUTFILE)
