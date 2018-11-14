import numpy as _np
from rpnpy.librmn import proto as _rp
from rpnpy.librmn.interp import _getCheckArg, _ftnf32, _list2ftnf32, _ftnOrEmpty
from rpnpy.librmn.interp import *

def gdxywdval(gdid, xpts, ypts, uuin, vvin, spdout=None, wdout=None):
    """
    Vectorial intepolation to points to speed/direction
    located at x-y coordinates

    Note that provided grid points coor. are considered
    to be Fortran indexing, from 1 to ni and from 1 to nj
    While numpy/C indexing starts from 0

    (spdout, wdout) = gdxywdval(gdid, xpts, ypts, uuin, vvin)
    (spdout, wdout) = gdxywdval(gdid, xpts, ypts, uuin, vvin, spdout, wdout)

    Args:
        gdid     : id of the grid(int or dict)
                   Dict with key 'id' is accepted from version 2.0.rc1
        xpts     : list of resquested points x-coor (list or numpy.ndarray)
        ypts     : list of resquested points y-coor (list or numpy.ndarray)
        uuin, vvin   : data to interpolate, on grid gdid (numpy.ndarray or dict)
                       Dict with key 'd' is accepted from version 2.0.rc1
        spdout, wdout : optional, interp.result array, same shape a xpts, ypts
                       (numpy.ndarray)
    Returns:
        numpy.ndarray, interpolation result, same shape a xpts, ypts
    Raises:
        TypeError    on wrong input arg types
        EzscintError on any other error

    Examples:
    >>> import os, os.path
    >>> import rpnpy.librmn.all as rmn
    >>>
    >>> # Read source data and define its grid
    >>> ATM_MODEL_DFILES = os.getenv('ATM_MODEL_DFILES')
    >>> myfile = os.path.join(ATM_MODEL_DFILES.strip(),'bcmk')
    >>> funit  = rmn.fstopenall(myfile)
    >>> uuRec  = rmn.fstlir(funit, nomvar='UU')
    >>> vvRec  = rmn.fstlir(funit, nomvar='VV')
    >>> inGrid = rmn.readGrid(funit, uuRec)
    >>> rmn.fstcloseall(funit)
    >>>
    >>> # Interpolate UV vectorially to a specific set of points
    >>> destPoints = ((148., 70.), (149., 71.))
    >>> xx = [x[0] for x in destPoints]
    >>> yy = [x[1] for x in destPoints]
    >>> (spd, wd) = rmn.gdxywdval(inGrid['id'], xx,yy, uuRec['d'], vvRec['d'])

    See Also:
        gdllsval
        gdxysval
        gdllvval
        gdxyvval
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
    gdid = _getCheckArg(int, gdid, gdid, 'id')
    uuin = _getCheckArg(_np.ndarray, uuin, uuin, 'd')
    vvin = _getCheckArg(_np.ndarray, vvin, vvin, 'd')
    gridParams = ezgxprm(gdid)
    uuin  = _ftnf32(uuin)
    vvin  = _ftnf32(vvin)
    if uuin.shape != gridParams['shape']:
        raise TypeError("gdllvval: Provided uuin array have inconsistent " +
                        "shape compered to the input grid")
    if vvin.shape != gridParams['shape']:
        raise TypeError("gdllvval: Provided vvin array have inconsistent " +
                        "shape compered to the input grid")
    cx = _list2ftnf32(xpts)
    cy = _list2ftnf32(ypts)
    if not (isinstance(cx, _np.ndarray) and isinstance(cy, _np.ndarray)):
        raise TypeError("xpts and ypts must be arrays")
    if cx.size != cy.size:
        raise TypeError(
            "provided xpts, ypts should have the same size")
    dshape = cx.shape
    spdout = _ftnOrEmpty(spdout, dshape, uuin.dtype)
    wdout = _ftnOrEmpty(wdout, dshape, uuin.dtype)
    if not (isinstance(spdout, _np.ndarray) and spdout.shape == dshape):
        raise TypeError("Wrong type,shape for uuout: %s, %s" %
                        (type(spdout), repr(dshape)))
    if not (isinstance(wdout, _np.ndarray) and wdout.shape == dshape):
        raise TypeError("Wrong type,shape for uuout: %s, %s" %
                        (type(wdout), repr(dshape)))
    istat = _rp.c_gdxywdval(gdid, spdout, wdout, uuin, vvin,
                           cx, cy, cx.size)
    if istat >= 0:
        return (spdout, wdout)
    raise EzscintError()

