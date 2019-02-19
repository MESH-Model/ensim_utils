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

def r2cfromflowinit(fstmatchgrid, fstfid, r2c):

	# Fetch initial flow fields including routing states.

	a = r2cattribute(AttributeName = 'QI1', AttributeUnits = 'i\"m**3 s**-1\"')
	r2cattributefromfst(a, fstmatchgrid, fstfid, fstnomvar = 'QI1', fstip1 = 0)
	r2c.attr.append(a)
	for ip3 in [ 0, 10, 20, 30 ]:
		a = r2cattribute(AttributeName = 'QO1', AttributeUnits = '\"m**3 s**-1\"')
		if (ip3 != 0):
			a.AttributeName = ('\"QO1 %d\"' % ip3)
		r2cattributefromfst(a, fstmatchgrid, fstfid, fstnomvar = 'QO1', fstip3 = ip3)
		r2c.attr.append(a)
	a = r2cattribute(AttributeName = 'STOR', AttributeUnits = 'm**3')
	r2cattributefromfst(a, fstmatchgrid, fstfid, fstnomvar = 'STOR', fstip1 = 0)
	r2c.attr.append(a)
	a = r2cattribute(AttributeName = 'OVER', AttributeUnits = 'm**2')
	r2cattributefromfst(a, fstmatchgrid, fstfid, fstnomvar = 'OVER', fstip1 = 0)
	r2c.attr.append(a)
	a = r2cattribute(AttributeName = 'LZS', AttributeUnits = 'mm')
	r2cattributefromfst(a, fstmatchgrid, fstfid, fstnomvar = 'LZS', fstip1 = 0)
	r2c.attr.append(a)

def r2ccreatevalinit(fstmatchgrid, fpathr2cout, fst = None):

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

	if (not fst is None):

		# Flow fields including routing states.

		r2cfromflowinit(fstmatchgrid, fst, r2c)

	# Write output.

	r2cfilecreateheader(r2c, fpathr2cout)
	r2cfileappendattributes(r2c, fpathr2cout)

def r2cfromfst_initial_values(

	# File names.

	FST_INFILE = '',
	R2C_OUTFILE = ''

	# Options.

	):

	# Stop if neither input file is defined.

	if ((FST_INFILE == '') or (not path.exists(FST_INFILE))):
		push_error('ERROR: Input file is not defined. The script cannot continue.')


	# Open fst files.

	if (path.exists(FST_INFILE)):
		fst = rmn.fstopenall(FST_INFILE)
		rec = rmn.fstlir(fst, etiket = 'WATR')
		if (rec is None):
			push_error('Records do not exist in ' + FST_INFILE + ' of etiket WATR. The script cannot continue.')
		fstgrid = rmn.readGrid(fst, rec)
		if (not 'dlat' in fstgrid) or (not 'dlon' in fstgrid):
			push_error('The grid of ' + FST_INFILE + ' must contain the dlat and dlon fields. The script cannot continue.')
	else:
		fst = None

	# Define the grid project.
	# Use the grid with the smallest delta.

	fstmatchgrid = fstgrid
	if (fstmatchgrid is None):
		push_error('No grid is defined. The script cannot continue.')

	# Create drainage database.

	if (R2C_OUTFILE != ''):
		r2ccreatevalinit(fstmatchgrid, fpathr2cout = R2C_OUTFILE, fst = fst)

	# Close fst files.

	if (not fst is None):
		rmn.fstcloseall(fst)

	# Recap messages.

	print('Recapping all messages ...')
	for m in messages:
		print(m)
