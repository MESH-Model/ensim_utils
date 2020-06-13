#!/usr/bin/python

# Required modules (standard packages).
#   - 'import os': For common I/O and path manipulation.
#   - 'import sys': To interpret command line arguments.
#   - 'import numpy as np':
#       Used for vectors and arrays, masking, and math functions.
import os
import sys
import numpy as np

# Required modules (standalone).
#   - 'from ensim_utils import *':
#       To read and write the drainage database file in 'r2c' format.
# 'ensim_utils':
#   'ensim_utils' is a standalone python script developed for MESH
#   applications that use EnSim Hydrologic file formats and cannot be
#   installed using a package manager or via 'pip'.
from ensim_utils import *

# Description: 'hybrid-db_ns-land-cover-fractions'
#   This script calculates land cover fractions from the LSS database
#   across the entire domain defined by the drainage database in a
#   hybrid resolution setup. To use the approach for a uniform setup,
#   set both the drainage and LSS databases equal to the input
#   drainage database file. Optionally, specify a streamflow input file
#   in tb0 format to derive fractions of sub-basins to the outlets at
#   the gauge locations.
#       This script only supports model database files in EnSim/Green
#   Kenue r2c format, and streamflow input files in EnSim/Green Kenue
#   tb0 format. It does not support reading other formats of these
#   files.
# Configurable conditions.
# Required:
#   - workdir:
#       Folder that contains the input drainage database file and where
#       the output file will be saved (default: current folder).
#   - input_drainage_database:
#       Name of the input drainage database file including extension
#       (default: 'MESH_drainage_database.r2c').
#   - input_lss_database:
#       Name of the input LSS database file including extension
#       (default: 'MESH_lss_database.r2c').
# Optional:
#   - input_streamflow:
#       Name of the input streamflow file including extension
#       (default: ''). Provided to calculate land cover fractions to
#       streamflow gauge locations. If not provided, fractions are
#       calculated for the entire domain.
#   - diagnostic_output:
#       Option to create intermediate output files (default: '').
# Update as necessary.
#   If run as a script at the terminal, arguments can be passed to
#   override these values in the script:
#       python hybrid-db_ns-land-cover-fractions.py input_streamflow=MESH_input_streamflow.tb0
workdir = '.'
input_drainage_database = 'MESH_drainage_database.r2c'
input_lss_database = 'MESH_lss_database.r2c'
input_streamflow = '' # Calculates land cover fractions for the entire domain if left blank.
diagnostic_output = 'yes'

# Override the above values with provided arguments.
override_arguments = sys.argv
if (len(override_arguments) > 1):
    for i, a in enumerate(override_arguments[1:]):
        argument = a.strip().split("=")
        if (len(argument) != 2):
            print("WARNING: Malformed argument: %s" % a)
        else:
            option = argument[0].lower()
            if (option == "workdir"):
                workdir = argument[1]
            elif (option == "input_drainage_database"):
                input_drainage_database = argument[1]
            elif (option == "input_lss_database"):
                input_lss_database = argument[1]
            elif (option == "input_streamflow"):
                input_streamflow = argument[1]
            elif (option == "diagnostic_output"):
                diagnostic_output = argument[1]
            else:
                print("WARNING: Unknown option: %s" % argument[0])

# Go to working folder.
os.chdir(workdir)

# Check if the input drainage database file exists.
if (not path.exists(input_drainage_database)):
    print("ERROR: The input file cannot be found: %s" % input_drainage_database)
    exit()

# Check if the input LSS database file exists (skip if the same as the
#   input drainage database file).
if (input_drainage_database != input_lss_database):
    if (not path.exists(input_lss_database)):
        print("ERROR: The input file cannot be found: %s" % input_lss_database)
        exit()

# Check if the optional input streamflow file exists (skip if blank).
if (input_streamflow != ""):
    if (not path.exists(input_streamflow)):
        print("ERROR: The input file cannot be found: %s" % input_streamflow)
        exit()

# Print a summary of the active options.
print("INFO: Work directory: %s" % workdir)
print("INFO: Input drainage database file: %s" % input_drainage_database)
if (input_drainage_database != input_lss_database):
    print("INFO: Input LSS database file: %s" % input_lss_database)
else:
    print("INFO: Input LSS database file: %s" % "(same as input drainage database file)")
if (input_streamflow != ""):
    print("INFO: Input streamflow file provided.")
    print("INFO: Input streamflow file: %s" % input_streamflow)
else:
    print("INFO: No input streamflow file provided.")
if (diagnostic_output != ''):
    print("INFO: Diagnostic output: yes")
else:
    print("INFO: Diagnostic output: no")

# Sanity checks for diagnostic output.
if (diagnostic_output.lower() == "no"):
    diagnostic_output = ''
if (diagnostic_output != ''):
    if (diagnostic_output == input_drainage_database):
        print("REMARK: Cannot create diagnostic output, it will overwrite the input drainage database file '%s'." % input_drainage_database)
        diagnostic_output = ''
    elif (diagnostic_output == input_lss_database):
        print("REMARK: Cannot create diagnostic output, it will overwrite the input drainage database file '%s'." % input_lss_database)
        diagnostic_output = ''

# Read the input drainage database file.
print("INFO: Reading %s." % input_drainage_database)
drainage_r2c = r2cfile()
r2cgridfromr2c(drainage_r2c, input_drainage_database)
r2cmetafromr2c(drainage_r2c, input_drainage_database)
r2cattributesfromr2c(drainage_r2c, input_drainage_database)

# Gather necessary attributes to derive information about the domain.
drainage_rank = []
drainage_next = []
drainage_area = []
drainage_xlng = []
drainage_ylat = []
for i, a in enumerate(drainage_r2c.attr):
    attribute_name = a.AttributeName.lower()
    if (attribute_name == "rank"):
        print("INFO: Found 'Rank' attribute at index %d." % (i + 1))
        drainage_rank = drainage_r2c.attr[i].AttributeData
    elif (attribute_name == "next"):
        print("INFO: Found 'Next' attribute at index %d." % (i + 1))
        drainage_next = drainage_r2c.attr[i].AttributeData
    elif (attribute_name == "gridarea"):
        print("INFO: Found 'GridArea' attribute at index %d." % (i + 1))
        drainage_area = drainage_r2c.attr[i].AttributeData
    elif (attribute_name == "longitude"):
        print("INFO: Found 'Longitude' attribute at index %d." % (i + 1))
        drainage_xlng = drainage_r2c.attr[i].AttributeData
    elif (attribute_name == "latitude"):
        print("INFO: Found 'Latitude' attribute at index %d." % (i + 1))
        drainage_ylat = drainage_r2c.attr[i].AttributeData

# Read the input LSS database file.
print("INFO: Reading %s." % input_lss_database)
lss_r2c = r2cfile()
r2cgridfromr2c(lss_r2c, input_lss_database)
r2cmetafromr2c(lss_r2c, input_lss_database)
r2cattributesfromr2c(lss_r2c, input_lss_database)

# Gather necessary attributes to derive information about the domain.
lss_rank = []
lss_xlng = []
lss_ylat = []
for i, a in enumerate(lss_r2c.attr):
    attribute_name = a.AttributeName.lower()
    if (attribute_name == "rank"):
        print("INFO: Found 'Rank' attribute at index %d." % (i + 1))
        lss_rank = lss_r2c.attr[i].AttributeData
    elif (attribute_name == "longitude"):
        print("INFO: Found 'Longitude' attribute at index %d." % (i + 1))
        lss_xlng = lss_r2c.attr[i].AttributeData
    elif (attribute_name == "latitude"):
        print("INFO: Found 'Latitude' attribute at index %d." % (i + 1))
        lss_ylat = lss_r2c.attr[i].AttributeData

# Get the number of GRUs.
gru_count = lss_r2c.meta.ClassCount
print("INFO: Found %d GRUs/land cover classifications active in the file (including impervious area)." % gru_count)

# Sanity checks.
if (gru_count < 2):
    print("ERROR: 'gru_count' cannot be less than 2.")
    exit()
if (drainage_rank == []):
    print("'Rank' was not found in the input drainage database file.")
    exit()
if (drainage_next == []):
    print("'Next' was not found in the input drainage database file.")
    exit()
if (drainage_area == []):
    print("'GridArea' was not found in the input drainage database file.")
    exit()
if (lss_rank == []):
    print("'Rank' was not found in the input LSS database file.")
    exit()

# Derive coordinates.
if (drainage_xlng == []):
    print("INFO: 'Longitude' field not found in input drainage database file. Deriving values.")
    if (not drainage_r2c.grid.Projection == 'LATLONG'):
        print("ERROR: Unsupported projection '%s'." % drainage_r2c.grid.Projection)
    else:
        drainage_xlng = np.empty((drainage_r2c.grid.xCount, drainage_r2c.grid.yCount))
        for x in range(drainage_r2c.grid.xCount):
            drainage_xlng[x, :] = (drainage_r2c.grid.xOrigin + drainage_r2c.grid.xDelta*(x + 1)) - drainage_r2c.grid.xDelta/2.0
if (drainage_ylat == []):
    print("INFO: 'Latitude' field not found in input drainage database file. Deriving values.")
    if (not drainage_r2c.grid.Projection == 'LATLONG'):
        print("ERROR: Unsupported projection '%s'." % drainage_r2c.grid.Projection)
    else:
        drainage_ylat = np.empty((drainage_r2c.grid.xCount, drainage_r2c.grid.yCount))
        for y in range(drainage_r2c.grid.yCount):
            drainage_ylat[:, y] = (drainage_r2c.grid.yOrigin + drainage_r2c.grid.yDelta*(y + 1)) - drainage_r2c.grid.yDelta/2.0
if (lss_xlng == []):
    print("INFO: 'Longitude' field not found in input LSS database file. Deriving values.")
    if (not lss_r2c.grid.Projection == 'LATLONG'):
        print("ERROR: Unsupported projection '%s'." % lss_r2c.grid.Projection)
    else:
        lss_xlng = np.empty((lss_r2c.grid.xCount, lss_r2c.grid.yCount))
        for x in range(lss_r2c.grid.xCount):
            lss_xlng[x, :] = (lss_r2c.grid.xOrigin + lss_r2c.grid.xDelta*(x + 1)) - lss_r2c.grid.xDelta/2.0
if (lss_ylat == []):
    print("INFO: 'Latitude' field not found in input drainage database file. Deriving values.")
    if (not lss_r2c.grid.Projection == 'LATLONG'):
        print("ERROR: Unsupported projection '%s'." % lss_r2c.grid.Projection)
    else:
        lss_ylat = np.empty((lss_r2c.grid.xCount, lss_r2c.grid.yCount))
        for y in range(lss_r2c.grid.yCount):
            lss_ylat[:, y] = (lss_r2c.grid.yOrigin + lss_r2c.grid.yDelta*(y + 1)) - lss_r2c.grid.yDelta/2.0

# Identify the final 'Rank' to accumulate fractions.
out_rank = []

# Optionally add locations from the input streamflow file.
if (input_streamflow != ""):

    # Read data from the file.
    print("INFO: Reading %s." % input_streamflow)
    streamflow_tb0 = tb0file()
    tb0projectionfromtb0(streamflow_tb0, input_streamflow)
    tb0metafromtb0(streamflow_tb0, input_streamflow)
    tb0columnsfromtb0(streamflow_tb0, input_streamflow)

    # Add 'Rank' where the locations intersect the drainage database
    #   domain.
    # This process derives a 1-based index.
    print("INFO: Calculating GRU/land cover fractions for these 'Rank' from the input streamflow file:")
    print("%s %s %s %s %s" % (''.rjust(8), 'GAUGE'.rjust(15), 'IY'.rjust(15), 'JX'.rjust(15), 'RANK'.rjust(15)))
    for i, a in enumerate(streamflow_tb0.cols):
        x = int((a.ColumnLocationX - drainage_r2c.grid.xOrigin)/drainage_r2c.grid.xDelta) + 1
        y = int((a.ColumnLocationY - drainage_r2c.grid.yOrigin)/drainage_r2c.grid.yDelta) + 1
        if (not drainage_rank[x - 1, y - 1] in out_rank):
            out_rank.append(drainage_rank[x - 1, y - 1])
        print("%s %s %s %s %s" %(str(i + 1).rjust(8), a.ColumnName[0:14].rjust(15), str(y).rjust(15), str(x).rjust(15), str(int(out_rank[i])).rjust(15)))

# Identify the final 'Rank' to accumulate fractions.
if (not drainage_r2c.meta.TotalNumOfGrids in out_rank):
    print("INFO: Calculating GRU/land cover fractions for the outlet of the domain:")
    print("%s %s %s %s %s" % (''.rjust(8), 'GAUGE'.rjust(15), 'IY'.rjust(15), 'JX'.rjust(15), 'RANK'.rjust(15)))
    (x, y) = np.where(drainage_rank == drainage_r2c.meta.TotalNumOfGrids)
    out_rank.append(drainage_r2c.meta.TotalNumOfGrids)
    print("%s %s %s %s %s" %(str(len(out_rank)).rjust(8), 'Domain Outlet'.rjust(15), str(int(y + 1)).rjust(15), str(int(x + 1)).rjust(15), str(int(drainage_r2c.meta.TotalNumOfGrids)).rjust(15)))

# Create an object-based 'case' class for cascading values.
class mapped_cell(object):
    def __init__(self, id, back):
        self.id = id
        self.back = back
        self.outlet = False
        self.value = None
    def PropagateValue(self, value):
        self.value = value
        if (not self.back is None):
            for i in self.back:
                if (not cells[int(i) - 1].outlet):
                    cells[int(i) - 1].PropagateValue(value)

# Build 'Rank' based working arrays.
print("INFO: Abstracting cells...")
cells = []
for i in range(drainage_r2c.meta.TotalNumOfGrids):
    (x, y) = np.where(drainage_rank == (i + 1))
    cells.append(mapped_cell(id = (i + 1), back = drainage_rank[np.where(drainage_next == (i + 1))]))

# Identify areas contributing to the locations of 'Rank'.
out_rank.sort(reverse = True)

# Mark gauge locations.
for i in out_rank:
    cells[int(i) - 1].outlet = True

# Identify subbasins.
print("INFO: Identifying subbasins...")
n = 1
for i in out_rank:
    cells[int(i) - 1].PropagateValue(n)
    n += 1
print("INFO: Completed.")

# Map the two domains.
print("INFO: Mapping domains...")
rankgeophytoshd = np.zeros((drainage_r2c.grid.xCount, drainage_r2c.grid.yCount))
geophydist = np.zeros((drainage_r2c.grid.xCount, drainage_r2c.grid.yCount))
geophydist[drainage_rank > 0] = sys.float_info.max
for n in range(drainage_r2c.meta.TotalNumOfGrids):
    (nx, ny) = np.where(drainage_rank == (n + 1))
    for i in range(lss_r2c.meta.TotalNumOfGrids):
        (ix, iy) = np.where(lss_rank == (i + 1))
        d = (lss_ylat[(ix, iy)] - drainage_ylat[(nx, ny)])**2 + (lss_xlng[(ix, iy)] - drainage_xlng[(nx, ny)])**2
        if (d < geophydist[(nx, ny)]):
            geophydist[(nx, ny)] = d
            rankgeophytoshd[(nx, ny)] = (i + 1)

if (diagnostic_output != ''):
    print("INFO: Saving diagnostic output 'shd_output.r2c'.")
    subbasins = np.zeros((drainage_r2c.grid.xCount, drainage_r2c.grid.yCount))
    for i, c in enumerate(cells):
        subbasins[np.where(drainage_rank == (i + 1))] = c.value
    r2c = r2cfile()
    r2cgridfromr2c(r2c, input_drainage_database)
    r2cmetafromr2c(r2c, input_drainage_database)
    r2cattributesfromr2c(r2c, input_drainage_database)
    r2c.attr.insert((len(r2c.attr) - r2c.meta.ClassCount), r2cattribute(AttributeName = 'GeophyDist', AttributeData = geophydist))
    r2c.attr.insert((len(r2c.attr) - r2c.meta.ClassCount), r2cattribute(AttributeName = 'RankGeophyToShd', AttributeType = 'integer', AttributeData = rankgeophytoshd))
    r2c.attr.insert((len(r2c.attr) - r2c.meta.ClassCount), r2cattribute(AttributeName = 'Subbasins', AttributeType = 'integer', AttributeData = subbasins))
    r2cfilecreateheader(r2c, 'shd_output.r2c')
    r2cfileappendattributes(r2c, 'shd_output.r2c')

# Print of script message.
print('\nProcessing has completed.')
