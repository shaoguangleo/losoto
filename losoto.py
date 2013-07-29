#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Authors:
# Francesco de Gasperin
# Cyril Tasse
# Reinout van Weeren
# Maaijke Mevius
# Bas van der Tol

import sys, os
import lofar.parameterset
import losoto.operations
import losoto._version
import losoto.ClassMakeHDF5

# Options
import optparse
opt = optparse.OptionParser(usage='%prog [-v] [-d gds] [-c clusterdesc] [-g globaldb]\
        parset [default: losoto.parset] \n Author: Francesco de Gasperin\
        (fdg@hs.uni-hamurg.de)', version='%prog '+losoto._version.__version__)
opt.add_option('-v', '--verbose', help='Go VeRbOsE! (default=False)', action='store_true', default=False)
opt.add_option('-d', '--gds', help='Comma separated list of gds files used to construct the globaldb', type='string', default='')
opt.add_option('-c', '--clusterdesc', help='Cluster desc file (needed if -d is active)', type='string', default='')
opt.add_option('-g', '--globaldb', help='Globaldb in HDF5 format', type='string', default='')
(options, args) = opt.parse_args()

verb = options.verbose
gdsFiles = options.gds.split(',')
globaldbFile = options.globaldb
clusterdesc = options.clusterdesc

# Check options
try: parsetFile = args[0]
except: parsetFile = 'losoto.parset'

if not os.path.isfile(parsetFile):
    print "Error: missing parset, I don't know what to do :'("
    sys.exit(1)

# Open the HDF5 or create it with ClassMakeHDF5()
H = losoto.ClassMakeHDF5.ClassMakeHDF5()
if os.path.isfile(globaldbFile):
    H.load_globaldb(globaldbFile)
elif all([os.path.isfile(gdsFile) for gdsFile in gdsFiles]) and os.path.isfile(clusterdesc):
    parmdbFile = H.load_gds(gdsFiles, clusterdesc, globaldb='globaldb', sky_name='sky', instrument_name='instrument', stations=[], sources=[])
    globaldbFile = H.create_HDF5(parmdbFile)
    H.load_globaldb(globaldbFile)
else:
    print "Error: missing/wrong solutions file, I don't know what to work on :'("
    sys.exit(1)

# from ~vdtol/Expion-2011-05-03/src
parset = lofar.parameterset.parameterset( parsetFile )
steps = parset.getStringVector( "LoSoTo.Steps", [] )

# Possible operations, linked to relative function
operations = { "RESET": losoto.operations.reset,
               "CLOCKTEC": losoto.operations.clocktec,
               "FLAG": losoto.operations.flag,
               "SMOOTH": losoto.operations.smooth,
               "INTERP": losoto.operations.interp,
               "PLOT": losoto.operations.plot,
               "APPLY": losoto.operations.apply }

for step in steps:
   operation = parset.getString( '.'.join( [ "LoSoTo.Steps", step, "Operation" ] ) )
   print "Info: Starting \'" + step + "\' step (operation: " + operation + ")."
   H = operations[ operation ] ( step, parset, H )

print "Done."
