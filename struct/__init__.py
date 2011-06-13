"""
This contains useful data structures and associated functions
"""
from .. import conf

# Unicode Strings -------------------------------------------------------------
# See Python's "aliases.py" for a list of possible encodings
UnicodeEncodings = (
    # Encodings we'll try for conversion to unicode
    'UTF8',     # Standard encoding
    'U16',      # Some files use UTF-16 though
    'cp1252',   # Western Europe
    'cp500',    # Western Europe
    'cp932',    # Japanese SJIS-win 
    'mbcs',     # Multi-byte character set (depends on the Windows locale)
    )
NumEncodings = len(UnicodeEncodings)

def Unicode(name,tryFirstEncoding=False):
    if not conf.useUnicode: return name #don't change if not unicode mode.
    if isinstance(name,unicode): return name
    if isinstance(name,str):
        if tryFirstEncoding:
            try:
                return unicode(name,tryFirstEncoding)
            except UnicodeDecodeError: 
                deprint("Unable to decode '%s' in %s." % (name, tryFirstEncoding))
                pass
        for i in range(NumEncodings):
            try:
                return unicode(name,UnicodeEncodings[i])
            except UnicodeDecodeError:
                if i == NumEncodings - 1:
                    raise
    return name

def Encode(name,tryFirstEncoding=False):
    if not conf.useUnicode: return name #don't change if not unicode mode.
    if isinstance(name,str): return name
    if isinstance(name,unicode):
        if tryFirstEncoding:
            try:
                return name.encode(tryFirstEncoding)
            except UnicodeEncodeError: 
                deprint("Unable to encode '%s' in %s." % (name, tryFirstEncoding))
                pass
        for i in range(NumEncodings):
            try:
                return name.encode(UnicodeEncodings[i])
            except UnicodeEncodeError:
                if i == NumEncodings - 1:
                    raise
    return name
