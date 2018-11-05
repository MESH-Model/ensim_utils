import numpy as _np
from rpnpy.librmn import proto as _rp
from rpnpy.librmn.interp import _getCheckArg, _ftnf32, _ftnOrEmpty
from rpnpy.librmn.interp import *

def ezwdint(gdidout, gdidin, uuin, vvin, spdout=None, wdout=None):
    """
    Vectorial horizontal interpolation to speed/direction

    (spdout, wdout) = ezwdint(gdidout, gdidin, uuin, vvin)
    (spdout, wdout) = ezwdint(gdidout, gdidin, uuin, vvin, spdout, wdout)

    Args:
        gdidout : output grid id (int or dict)
                  Dict with key 'id' is accepted from version 2.0.rc1
        gdidid  : grid id describing uuin grid (int or dict)
                  Dict with key 'id' is accepted from version 2.0.rc1
        uuin    : data x-part to interpolate (numpy.ndarray or dict)
                  Dict with key 'd' is accepted from version 2.0.rc1
        vvin    : data y-part to interpolate (numpy.ndarray or dict)
                  Dict with key 'd' is accepted from version 2.0.rc1
        spdout  : interp.result array speed (numpy.ndarray or dict)
                  Dict with key 'd' is accepted from version 2.0.rc1
        wdout   : interp.result array direction (numpy.ndarray or dict)
                  Dict with key 'd' is accepted from version 2.0.rc1
    Returns:
        interpolation result (numpy.ndarray, numpy.ndarray)
    Raises:
        TypeError    on wrong input arg types
        EzscintError on any other error

    Examples:
    >>> import os, os.path
    >>> import rpnpy.librmn.all as rmn
    >>>
    >>> # Read source data and define its grid
    >>> ATM_MODEL_DFILES = os.getenv('ATM_MODEL_DFILES')
    >>> myfile = os.path.join(ATM_MODEL_DFILES.strip(),'bcmk','2009042700_000')
    >>> funit  = rmn.fstopenall(myfile)
    >>> uuRec  = rmn.fstlir(funit, nomvar='UU')
    >>> vvRec  = rmn.fstlir(funit, nomvar='VV', ip1=uuRec['ip1'], ip2=uuRec['ip2'])
    >>> inGrid = rmn.readGrid(funit, uuRec)
    >>> rmn.fstcloseall(funit)
    >>>
    >>> # Define a destination Grid
    >>> (ni, nj, lat0, lon0, dlat, dlon) = (200, 100, 35.,265.,0.25,0.25)
    >>> outGrid  = rmn.defGrid_L(ni, nj, lat0, lon0, dlat, dlon)
    >>>
    >>> # Interpolate U/V vectorially
    >>> (spd, wd) = rmn.ezwdint(outGrid['id'], inGrid['id'], uuRec['d'], vvRec['d'])

    See Also:
        ezsint
        ezuvint
        ezsetopt
        rpnpy.librmn.const
        rpnpy.librmn.fstd98.fstopenall
        rpnpy.librmn.fstd98.fstlir
        rpnpy.librmn.fstd98.fstcloseall
        rpnpy.librmn.grids.readGrid
        rpnpy.librmn.grids.defGrid_L
        rpnpy.librmn.grids.encodeGrid
    """
    gdidout = _getCheckArg(int, gdidout, gdidout, 'id')
    gdidin  = _getCheckArg(int, gdidin,  gdidin , 'id')
    uuin    = _getCheckArg(_np.ndarray, uuin, uuin, 'd')
    vvin    = _getCheckArg(_np.ndarray, vvin, vvin, 'd')
    spdout  = _getCheckArg(None, spdout, spdout, 'd')
    wdout   = _getCheckArg(None, wdout, wdout, 'd')
    gridsetid = ezdefset(gdidout, gdidin)
    gridParams = ezgxprm(gdidin)
    uuin  = _ftnf32(uuin)
    vvin  = _ftnf32(vvin)
    if uuin.shape != gridParams['shape'] or vvin.shape != gridParams['shape']:
        raise TypeError("ezuvint: Provided uuin, vvin array have " +
                        "inconsistent shape compared to the input grid")
    dshape = ezgprm(gdidout)['shape']
    spdout = _ftnOrEmpty(spdout, dshape, uuin.dtype)
    wdout = _ftnOrEmpty(wdout, dshape, uuin.dtype)
    if not (isinstance(spdout, _np.ndarray) and
            isinstance(wdout, _np.ndarray)):
        raise TypeError("ezwdint: Expecting spdout, wdout of type " +
                        "numpy.ndarray, Got %s" % (type(spdout)))
    if spdout.shape != dshape or wdout.shape != dshape:
        raise TypeError("ezuvint: Provided spdout, wdout array have " +
                        "inconsistent shape compered to the output grid")
    istat = _rp.c_ezwdint(spdout, wdout, uuin, vvin)
    if istat >= 0:
        return (spdout, wdout)
    raise EzscintError()

