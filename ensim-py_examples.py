#!/usr/bin/python
# Required modules (standard packages).
#   - 'import os': For common I/O and path manipulation.
#   - 'import sys': To interpret command line arguments.
#   - 'import numpy as np':
#       Used for vectors and arrays, masking, and math functions.
#   - 'import from time import strftime': Date/time format.
import os
import sys
import numpy as np
from time import strftime

# Required modules (standalone).
#   - 'from ensim_utils import *':
#       To read and write the drainage database file in 'r2c' format.
# 'ensim_utils':
#   'ensim_utils' is a standalone python script developed for MESH
#   applications that use EnSim Hydrologic file formats and cannot be
#   installed using a package manager or via 'pip'.
from ensim_utils import *

# Documented example: Get 'DA' (drainage area) field.
print("INFO: Example 1 - Get 'DA' (drainage area) field from input drainage database file.")

# Input variables:
#   - input_drainage_database:
#       Name of the input drainage database file including extension
#       (default: 'MESH_drainage_database.r2c').
input_drainage_database = 'MESH_drainage_database.r2c'

# Check if the input drainage database file exists.
if (not path.exists(input_drainage_database)):
    print("ERROR: The input file cannot be found: %s" % input_drainage_database)
    exit()

# Print a summary of the active options.
print("INFO: Input drainage database file: %s" % input_drainage_database)

# Read the input drainage database file.
print("INFO: Reading %s." % input_drainage_database)
drainage_r2c = r2cfile()
r2cgridfromr2c(drainage_r2c, input_drainage_database)
r2cmetafromr2c(drainage_r2c, input_drainage_database)
r2cattributesfromr2c(drainage_r2c, input_drainage_database)

# Gather necessary attributes to derive information about the domain.
drainage_area = []
for i, a in enumerate(drainage_r2c.attr):
    attribute_name = a.AttributeName.lower()
    if (attribute_name == "da"):
        print("INFO: Found 'DA' attribute at index %d." % (i + 1))
        drainage_area = drainage_r2c.attr[i].AttributeData

# Sanity checks.
if (drainage_area == []):
    print("'GridArea' was not found in the input drainage database file.")
    exit()

# End of documented example.
# This example compacted to just the basic commands:
print("INFO: Re-running 'Example 1' (basic commands only)...")
drainage_r2c = r2cfile()
r2cgridfromr2c(drainage_r2c, input_drainage_database)
r2cattributesfromr2c(drainage_r2c, input_drainage_database)
drainage_area = []
for i, a in enumerate(drainage_r2c.attr):
    if (a.AttributeName.lower() == "da"):
        drainage_area = drainage_r2c.attr[i].AttributeData
print("INFO: Complete.")

# Print some indicative items from the data to illustrate the field...
print("DEBUG: Maximum value of the 'DA' attribute: %g" % np.max(drainage_area))
print("DEBUG: Minimum non-zero value of the 'DA' attribute: %g" % np.min(drainage_area[drainage_area > 0.0]))
print("INFO: End of 'Example 1'.")

# Documented example: Read 'QO' field from "QO_H.r2c" output file.
print("INFO: Example 2 - Read 'QO' field from input data file.")

# Input variables:
#   - input_data_file:
#       Name of the input data file including extension (default:
#       'QO_H.r2c').
input_data_file = 'QO_H.r2c'

# Check if the input data file exists.
if (not path.exists(input_data_file)):
    print("ERROR: The input file cannot be found: %s" % input_data_file)
    exit()

# Print a summary of the active options.
print("INFO: Input data file: %s" % input_data_file)

# Read header information from the file.
print("INFO: Reading %s." % input_data_file)
qo_r2c = r2cfile()
r2cgridfromr2c(qo_r2c, input_data_file)

# Read the time-series from the file (this process can take a while).
print("INFO: Reading all records from file...")
r2cattributesfromr2c(qo_r2c, input_data_file)
print("INFO: Complete.")

# End of documented example.
# This example compacted to just the basic commands:
print("INFO: Re-running 'Example 2' (basic commands only)...")
qo_r2c = r2cfile()
r2cgridfromr2c(qo_r2c, input_data_file)
r2cattributesfromr2c(qo_r2c, input_data_file)
print("INFO: Complete.")

# Print some indicative items from the data to illustrate the field...
print("DEBUG: Number of records read from file: %d" % qo_r2c.attr[0].FrameCount)
if (qo_r2c.attr[0].FrameCount > 0):
    i = qo_r2c.attr[0].AttributeData.index.min()
    c = strftime('%Y/%m/%d %H:%M:%S', i.timetuple())
    print("DEBUG: Earliest frame in time-series: %s" % c)
    print("DEBUG: Latest frame in time-series: %s" % strftime('%Y/%m/%d %H:%M:%S', qo_r2c.attr[0].AttributeData.index.max().timetuple()))
    d = qo_r2c.attr[0].AttributeData['Values'].loc[i] # Using a 'datetime' object directly.
    print("DEBUG: Minimum value greater than zero in frame '%s': %g" % (c, np.min(d[d > 0.0])))
    print("DEBUG: Maximum value in in frame '%s': %g" % (c, np.max(d[d > 0.0])))
    print("DEBUG: Average of values greater than zero in frame '%s': %g" % (c, np.mean(d[d > 0.0])))
    d = qo_r2c.attr[0].AttributeData['Values'].loc[c] # Using date provided as a string, e.g., 2002/01/01 00:00.
    print("DEBUG: Median of values greater than zero in frame '%s': %g" %(c, np.median(d[d > 0.0])))
print("INFO: End of 'Example 2'.")
