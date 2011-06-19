import StringIO
import cStringIO

from .. import conf

#------------------------------------------------------------------------------
from path import Path, GPath
from const import startupinfo
from unicode import Unicode, Encode

#------------------------------------------------------------------------------

def getStringBuffer(*args):
    """
    This gets the fastest buffer, given that the cStringIO doesn't work
    with uniocde
    """
    if conf.useUnicode:
        return StringIO.StringIO(*args)
    return cStringIO.StringIO(*args)

