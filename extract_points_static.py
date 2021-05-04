#!/usr/bin/python
from os import path
#from time import gmtime, strftime
#from datetime import datetime
#from dateutil import relativedelta as dt, tz, parser as dtparser
import numpy as np
import csv
import rpnpy.librmn.all as rmn
from ensim_utils import *
from file_locations import *

# To load rpnpy:
# . s.ssmuse.dot ENV/py/2.7/rpnpy/2.0.4

# Read locations from file.
na = []
la = []
lo = []
with open('station_locations.csv', 'rb') as f:
	reader = csv.reader(f)
	columns = next(reader)
	colmap = dict(zip(columns, range(len(columns))))
	for row in reader:
		na.append(row[colmap['Station']])
		la.append(row[colmap['Latitude']])
		lo.append(row[colmap['Longitude']])

# Fields.
PROCESS_FSTCONVFLD = []
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'orography_m_interp-nearest', fstnomvar = 'ME', AttributeName = 'Model_orography', AttributeUnits = 'm', intpopt = rmn.EZ_INTERP_NEAREST))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'orography_m_interp-linear', fstnomvar = 'ME', AttributeName = 'Model_orography', AttributeUnits = 'm', intpopt = rmn.EZ_INTERP_LINEAR))
PROCESS_FSTCONVFLD.append(conversionfieldfromfst(fname = 'orography_m_interp-cubic', fstnomvar = 'ME', AttributeName = 'Model_orography', AttributeUnits = 'm', intpopt = rmn.EZ_INTERP_CUBIC))
FILE_LABEL = ['geophy_yy25km', 'geophy_gu25km'] #'geophy_YY15km_mgUSGS_fillz0zp'

# Loop.
for f in FILE_LABEL:
	
	# Source file.
	fstfid = rmn.fstopenall(('%s.fst' % f))
	
	# Records.
	for i, c in enumerate(PROCESS_FSTCONVFLD):
	
		# Open and write 'meta' output.
		with open(('%s_%s.meta' % (f, c.fname)), 'wb') as t:
			if (not c.AttributeName is None):
				t.write('%s %s\n' % ('AttributeName:', c.AttributeName))
			if (not c.AttributeType is None):
				t.write('%s %s\n' % ('AttributeType:', c.AttributeType))
			if (not c.AttributeUnits is None):
				t.write('%s %s\n' % ('AttributeUnits:', c.AttributeUnits))
				t.write('Field = min(max(%g*Source + %g), %g), %g)\n' % (c.constmul, c.constadd, c.constrmin, c.constrmax))
			t.close()
		
		# Open and write header for 'data' output.
		c.fid = csv.writer(open(('%s_%s.csv' % (f, c.fname)), 'wb'))
		c.fid.writerow(np.concatenate((['Station'], na)))
		c.fid.writerow(np.concatenate((['Latitude'], la)))
		c.fid.writerow(np.concatenate((['Longitude'], lo)))
		
		# Save field.
		rec = latlonvalfromfst(la, lo, fstfid, fstnomvar = c.fstnomvar, fstetiket = c.fstetiket, fstip1 = c.fstip1, intpopt = c.intpopt, constmul = c.constmul, constadd = c.constadd, constrmax = c.constrmax, constrmin = c.constrmin)
		c.fid.writerow(np.concatenate((['0000-00-00 00:00'], rec)))
	
	# Close the file.
	rmn.fstcloseall(fstfid)
