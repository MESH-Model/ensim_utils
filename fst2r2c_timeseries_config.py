#!/usr/bin/python

from fst2r2c_timeseries import *
from dateutil import tz

# To load rpnpy:
# . s.ssmuse.dot ENV/py/2.7/rpnpy/2.0.4

# Process files.

r2ctimeseriesfromfst(
	R2CSHED_INFILE = 'header.r2c',
)
