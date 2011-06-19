import os
import subprocess

#-- To make commands executed with Popen hidden
startupinfo = None #default, required for non nt systems
if os.name == 'nt':
    startupinfo = subprocess.STARTUPINFO()
    try: startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    except:
        import _subprocess
        startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW

