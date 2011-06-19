"""
Contains wrye's wrapper around the os.path functions
"""

import os
import shutil
import re
import time
from subprocess import Popen, PIPE
from binascii import crc32

from .. import conf
from ..localization import _
from ..log import deprint
from ..error import StateError

from unicode import Encode, Unicode
from const import startupinfo

# Paths -----------------------------------------------------------------------
#------------------------------------------------------------------------------
_gpaths = {}
Path = None
def GPath(name):
    """Returns common path object for specified name/path."""
    if name is None:
        return None
    elif not name:
        norm = name
    elif isinstance(name,Path):
        norm = name._s
    else:
        norm = os.path.normpath(name)

    path = _gpaths.get(norm)
    if path != None:
        return path
    else:
        return _gpaths.setdefault(norm,Path(norm))

#------------------------------------------------------------------------------
class Path(object):
    """A file path. May be just a directory, filename or full path."""
    """Paths are immutable objects that represent file directory paths."""

    #--Class Vars/Methods -------------------------------------------
    norm_path = {} #--Dictionary of paths
    mtimeResets = [] #--Used by getmtime
    ascii = '[\x00-\x7F]'
    japanese_hankana = '[\xA1-\xDF]'
    japanese_zenkaku ='[\x81-\x9F\xE0-\xFC][\x40-\x7E\x80-\xFC]'
    reChar = re.compile('('+ascii+'|'+japanese_hankana+'|'+japanese_zenkaku+')', re.M)

    @staticmethod
    def get(name):
        """Returns path object for specified name/path."""
        if isinstance(name,Path): norm = name._s
        else: norm = os.path.normpath(name)
        return Path.norm_path.setdefault(norm,Path(norm))

    @staticmethod
    def getNorm(name):
        """Return the normpath for specified name/path object."""
        if not name: return name
        elif isinstance(name,Path): return name._s
        else: return os.path.normpath(name)

    @staticmethod
    def getCase(name):
        """Return the normpath+normcase for specified name/path object."""
        if not name: return name
        if isinstance(name,Path): return name._cs
        else: return os.path.normcase(os.path.normpath(name))

    @staticmethod
    def getcwd():
        return Path(os.getcwd())

    def setcwd(self):
        """Set cwd. Works as either instance or class method."""
        if isinstance(self,Path): dir = self._s
        else: dir = self
        os.chdir(dir)

    @staticmethod
    def mbSplit(path):
        """Split path to consider multibyte character boundary."""
        # Should also add Chinese fantizi and zhengtizi, Korean Hangul, etc.
        match = Path.reChar.split(path)
        result = []
        curResult = ''
        resultAppend = result.append
        for c in match:
            if c == '\\':
                resultAppend(curResult)
                curResult = ''
            else:
                curResult += c
        resultAppend(curResult)
        return result

    #--Instance stuff --------------------------------------------------
    #--Slots: _s is normalized path. All other slots are just pre-calced
    #  variations of it.
    __slots__ = ('_s','_cs','_csroot','_sroot','_shead','_stail','_ext','_cext','_sbody','_csbody')

    def __init__(self, name):
        """Initialize."""
        if conf.useUnicode:
            if isinstance(name,Path):
                self.__setstate__(unicode(name._s,'UTF8'))
            elif isinstance(name,unicode):
                self.__setstate__(name)
            else:
                self.__setstate__(Unicode(name))
                ##try:
                ##    self.__setstate__(unicode(str(name),'UTF8'))
                ##except UnicodeDecodeError:
                ##    try:
                ##        # A fair number of file names require UTF16 instead...
                ##        self.__setstate__(unicode(str(name),'U16'))
                ##    except UnicodeDecodeError:
                ##        try:
                ##            self.__setstate__(unicode(str(name),'cp1252'))
                ##        except UnicodeDecodeError:
                ##            # and one really really odd one (in SOVVM mesh bundle) requires cp500 (well at least that works unlike UTF8,16,32,32BE (the others I tried first))!
                ##            self.__setstate__(unicode(str(name),'cp500'))
        else:
            if isinstance(name,Path):
                self.__setstate__(name._s)
            elif isinstance(name,unicode):
                self.__setstate__(name)
            else:
                self.__setstate__(str(name))

    def __getstate__(self):
        """Used by pickler. _cs is redundant,so don't include."""
        return self._s

    def __setstate__(self,norm):
        """Used by unpickler. Reconstruct _cs."""
        self._s = norm
        self._cs = os.path.normcase(self._s)
        self._sroot,self._ext = os.path.splitext(self._s)
        if conf.useUnicode:
            self._shead,self._stail = os.path.split(self._s)
        else:
            pathParts = Path.mbSplit(self._s)
            if len(pathParts) == 1:
                self._shead = ''
                self._stail = pathParts[0]
            else:
                self._shead = '\\'.join(pathParts[0:-1])
                self._stail = pathParts[-1]
        self._cext = os.path.normcase(self._ext)
        self._csroot = os.path.normcase(self._sroot)
        self._sbody = os.path.basename(os.path.splitext(self._s)[0])
        self._csbody = os.path.normcase(self._sbody)

    def __len__(self):
        return len(self._s)

    def __repr__(self):
        return "wryebase.util.path.Path("+repr(self._s)+")"

    def __str__(self):
        return self._s
    #--Properties--------------------------------------------------------
    #--String/unicode versions.
    @property
    def s(self):
        "Path as string."
        return self._s
    @property
    def cs(self):
        "Path as string in normalized case."
        return self._cs
    @property
    def csroot(self):
        "Root as string."
        return self._csroot
    @property
    def sroot(self):
        "Root as string."
        return self._sroot
    @property
    def shead(self):
        "Head as string."
        return self._shead
    @property
    def stail(self):
        "Tail as string."
        return self._stail
    @property
    def sbody(self):
        "For alpha\beta.gamma returns beta as string."
        return self._sbody
    @property
    def csbody(self):
        "For alpha\beta.gamma returns beta as string in normalized case."
        return self._csbody

    #--Head, tail
    @property
    def headTail(self):
        "For alpha\beta.gamma returns (alpha,beta.gamma)"
        return map(GPath,(self._shead,self._stail))
    @property
    def head(self):
        "For alpha\beta.gamma, returns alpha."
        return GPath(self._shead)
    @property
    def tail(self):
        "For alpha\beta.gamma, returns beta.gamma."
        return GPath(self._stail)
    @property
    def body(self):
        "For alpha\beta.gamma, returns beta."
        return GPath(self._sbody)

    #--Root, ext
    @property
    def rootExt(self):
        return (GPath(self._sroot),self._ext)
    @property
    def root(self):
        "For alpha\beta.gamma returns alpha\beta"
        return GPath(self._sroot)
    @property
    def ext(self):
        "Extension (including leading period, e.g. '.txt')."
        return self._ext
    @property
    def cext(self):
        "Extension in normalized case."
        return self._cext
    @property
    def temp(self):
        "Temp file path.."
        return self+'.tmp'
    @property
    def backup(self):
        "Backup file path."
        return self+'.bak'

    #--size, atim, ctime
    @property
    def size(self):
        "Size of file or directory."
        if self.isdir():
            join = os.path.join
            getSize = os.path.getsize
            try:
                return sum([sum(map(getSize,map(lambda z: join(x,z),files))) for x,y,files in os.walk(self._s)])
            except ValueError:
                return 0
        else:
            return os.path.getsize(self._s)
    @property
    def atime(self):
        return os.path.getatime(self._s)
    @property
    def ctime(self):
        return os.path.getctime(self._s)

    #--Mtime
    def getmtime(self,maxMTime=False):
        """Returns mtime for path. But if mtime is outside of epoch, then resets
        mtime to an in-epoch date and uses that."""
        if self.isdir() and maxMTime:
            #fastest implementation I could make
            c = []
            cExtend = c.extend
            join = os.path.join
            getM = os.path.getmtime
            [cExtend([getM(join(root,dir)) for dir in dirs] + [getM(join(root,file)) for file in files]) for root,dirs,files in os.walk(self._s)]
            try:
                return max(c)
            except ValueError:
                return 0
        mtime = int(os.path.getmtime(self._s))
        #--Y2038 bug? (os.path.getmtime() can't handle years over unix epoch)
        if mtime <= 0:
            import random
            #--Kludge mtime to a random time within 10 days of 1/1/2037
            mtime = time.mktime((2037,1,1,0,0,0,3,1,0))
            mtime += random.randint(0,10*24*60*60) #--10 days in seconds
            self.mtime = mtime
            Path.mtimeResets.append(self)
        return mtime
    def setmtime(self,mtime):
        os.utime(self._s,(self.atime,int(mtime)))
    mtime = property(getmtime,setmtime,doc="Time file was last modified.")

    #--crc
    @property
    def crc(self):
        """Calculates and returns crc value for self."""
        size = self.size
        crc = 0L
        ins = self.open('rb')
        insRead = ins.read
        while ins.tell() < size:
            crc = crc32(insRead(512),crc)
        ins.close()
        return crc & 0xffffffff

    #--crc with progress bar
    def crcProgress(self, progress):
        """Calculates and returns crc value for self, updating progress as it goes."""
        size = self.size
        progress.setFull(max(size,1))
        crc = 0L
        with self.open('rb') as ins:
            insRead = ins.read
            while ins.tell() < size:
                crc = crc32(insRead(2097152),crc) # 2MB at a time, probably ok
                progress(ins.tell())
        return crc & 0xFFFFFFFF

    #--Path stuff -------------------------------------------------------
    #--New Paths, subpaths
    def __add__(self,other):
        return GPath(self._s + Path.getNorm(other))
    def join(*args):
        norms = [Path.getNorm(x) for x in args]
        return GPath(os.path.join(*norms))
    def list(self):
        """For directory: Returns list of files."""
        if not os.path.exists(self._s): return []
        return [GPath(x) for x in os.listdir(self._s)]
    def walk(self,topdown=True,onerror=None,relative=False):
        """Like os.walk."""
        if relative:
            start = len(self._s)
            return ((GPath(x[start:]),[GPath(u) for u in y],[GPath(u) for u in z])
                for x,y,z in os.walk(self._s,topdown,onerror))
        else:
            return ((GPath(x),[GPath(u) for u in y],[GPath(u) for u in z])
                for x,y,z in os.walk(self._s,topdown,onerror))
    def split(self):
        """Splits the path into each of it's sub parts.  IE: C:\Program Files\Bethesda Softworks
           would return ['C:','Program Files','Bethesda Softworks']"""
        dirs = []
        drive, path = os.path.splitdrive(self.s)
        path = path.strip(os.path.sep)
        l,r = os.path.split(path)
        while l != '':
            dirs.append(r)
            l,r = os.path.split(l)
        dirs.append(r)
        if drive != '':
            dirs.append(drive)
        dirs.reverse()
        return dirs
    def relpath(self,path):
        try:
            return GPath(os.path.relpath(self._s,Path.getNorm(path)))
        except:
            # Python 2.5 doesn't have os.path.relpath, so we'll have to implement our own
            path = GPath(path)
            if path.isfile(): path = path.head
            splitSelf = self.split()
            splitOther = path.split()
            relPath = []
            while len(splitSelf) > 0 and len(splitOther) > 0 and splitSelf[0] == splitOther[0]:
                splitSelf.pop(0)
                splitOther.pop(0)
            while len(splitOther) > 0:
                splitOther.pop(0)
                relPath.append('..')
            relPath.extend(splitSelf)
            return GPath(os.path.join(*relPath))

    #--File system info
    #--THESE REALLY OUGHT TO BE PROPERTIES.
    def exists(self):
        return os.path.exists(self._s)
    def isdir(self):
        return os.path.isdir(self._s)
    def isfile(self):
        return os.path.isfile(self._s)
    def isabs(self):
        return os.path.isabs(self._s)

    #--File system manipulation
    def open(self,*args):
        if self._shead and not os.path.exists(self._shead):
            os.makedirs(self._shead)
        return open(self._s,*args)
    def makedirs(self):
        if not self.exists(): os.makedirs(self._s)
    def remove(self):
        if self.exists(): os.remove(self._s)
    def removedirs(self):
        if self.exists(): os.removedirs(self._s)
    def rmtree(self,safety='PART OF DIRECTORY NAME'):
        """Removes directory tree. As a safety factor, a part of the directory name must be supplied."""
        if self.isdir() and safety and safety.lower() in self._cs:
            # Clear ReadOnly flag if set
            cmd = r'attrib -R "%s\*" /S /D' % (self._s)
            cmd = Encode(cmd,'mbcs')
            ins, err = Popen(cmd, stdout=PIPE, startupinfo=startupinfo).communicate()
            shutil.rmtree(self._s)

    #--start, move, copy, touch, untemp
    def start(self, exeArgs=None):
        """Starts file as if it had been doubleclicked in file explorer."""
        if self._cext == '.exe':
            if not exeArgs:
                subprocess.Popen([self.s], close_fds=True)
            else:
                subprocess.Popen(exeArgs, executable=self.s, close_fds=True)
        else:
            os.startfile(self._s)
    def copyTo(self,destName):
        destName = GPath(destName)
        if self.isdir():
            shutil.copytree(self._s,destName._s)
        else:
            if destName._shead and not os.path.exists(destName._shead):
                os.makedirs(destName._shead)
            shutil.copyfile(self._s,destName._s)
            destName.mtime = self.mtime
    def moveTo(self,destName):
        if not self.exists():
            raise StateError(self._s + _(" cannot be moved because it does not exist."))
        destPath = GPath(destName)
        if destPath._cs == self._cs: return
        if destPath._shead and not os.path.exists(destPath._shead):
            os.makedirs(destPath._shead)
        elif destPath.exists():
            os.remove(destPath._s)
        shutil.move(self._s,destPath._s)
    def touch(self):
        """Like unix 'touch' command. Creates a file with current date/time."""
        if self.exists():
            self.mtime = time.time()
        else:
            self.temp.open('w').close()
            self.untemp()
    def untemp(self,doBackup=False):
        """Replaces file with temp version, optionally making backup of file first."""
        if self.temp.exists():
            if self.exists():
                if doBackup:
                    self.backup.remove()
                    shutil.move(self._s, self.backup._s)
                else:
                    os.remove(self._s)
            shutil.move(self.temp._s, self._s)

    #--Hash/Compare
    def __hash__(self):
        return hash(self._cs)
    def __cmp__(self, other):
        if isinstance(other,Path):
            try:
                return cmp(self._cs, other._cs)
            except UnicodeDecodeError:
                try:
                    return cmp(Encode(self._cs), Encode(other._cs))
                except UnicodeError:
                    deprint("Wrye Bash Unicode mode is currently %s" % (['off.','on.'][conf.useUnicode]))
                    deprint("unrecovered Unicode error when dealing with %s - presuming non equal." % (self._cs))
                    return False
        else:
            try:
                return cmp(self._cs, Path.getCase(other))
            except UnicodeDecodeError:
                try:
                    return cmp(Encode(self._cs), Encode(Path.getCase(other)))
                except UnicodeError:
                    deprint("Wrye Bash Unicode mode is currently %s." % (['off','on'][conf.useUnicode]))
                    deprint("unrecovered Unicode error when dealing with %s - presuming non equal.'" % (self._cs))
                    return False

