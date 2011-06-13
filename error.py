from __future__ import with_statement

import wryebase.conf
from wryebase.localization import _

class BoltError(Exception):
    """Generic error with a string message."""
    def __init__(self,message):
        self.message = message
    def __str__(self):
        return self.message


class PermissionError(BoltError):
    """Wrye Bash doesn't have permission to access the specified file/directory."""
    def __init__(self,message=None):
        message = message or _('Access is denied.')
        BoltError.__init__(self,message)


class SkipError(BoltError):
    """User pressed 'Skip' on the progress meter."""
    def __init__(self,message=_('Action skipped by user.')):
        BoltError.__init__(self,message)


class CancelError(BoltError):
    """User pressed 'Cancel' on the progress meter."""
    def __init__(self,message=_('Action aborted by user.')):
        BoltError.__init__(self, message)


class UncodedError(BoltError):
    """Coding Error: Call to section of code that hasn't been written."""
    def __init__(self,message=_('Section is not coded yet.')):
        BoltError.__init__(self,message)


class StateError(BoltError):
    """Error: Object is corrupted."""
    def __init__(self,message=_('Object is in a bad state.')):
        BoltError.__init__(self,message)


class ArgumentError(BoltError):
    """Coding Error: Argument out of allowed range of values."""
    def __init__(self,message=_('Argument is out of allowed ranged of values.')):
        BoltError.__init__(self,message)


class AbstractError(BoltError):
    """Coding Error: Abstract code section called."""
    def __init__(self,message=_('Abstract section called.')):
        BoltError.__init__(self,message)
