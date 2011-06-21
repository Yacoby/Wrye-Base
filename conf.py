"""
This holds common config files. This is bad and needs to be removed as it is
a dependcy everywhere and could probably be handled in a far better way
"""

"""This shouldn't exist. The entire program should be unicode"""
useUnicode = False

"""
It would probably be better to use a logging class for this. A logging clas
would allow far more flexibility and also allows us to hide the global leading
to a more elegant solution
"""
deprintOn = False
