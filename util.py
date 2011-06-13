import os
import subprocess
import StringIO
import cStringIO

import conf

def getStringBuffer(*args):
    """
    This gets the fastest buffer, given that the cStringIO doesn't work
    with uniocde
    """
    if conf.useUnicode:
        return StringIO.StringIO(*args)
    return StringIO.StringIO(*args)

#-- To make commands executed with Popen hidden
startupinfo = None #default, required for non nt systems
if os.name == 'nt':
    startupinfo = subprocess.STARTUPINFO()
    try: startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    except:
        import _subprocess
        startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
