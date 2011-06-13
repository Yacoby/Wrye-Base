"""
This contains log and debug related functions
"""
import conf

class Log:
    """Log Callable. This is the abstract/null version. Useful version should
    override write functions.

    Log is divided into sections with headers. Header text is assigned (through
    setHeader), but isn't written until a message is written under it. I.e.,
    if no message are written under a given header, then the header itself is
    never written."""

    def __init__(self):
        """Initialize."""
        self.header = None
        self.prevHeader = None

    def setHeader(self,header,writeNow=False,doFooter=True):
        """Sets the header."""
        self.header = header
        if self.prevHeader:
            self.prevHeader += 'x'
        self.doFooter = doFooter
        if writeNow: self()

    def __call__(self,message=None):
        """Callable. Writes message, and if necessary, header and footer."""
        if self.header != self.prevHeader:
            if self.prevHeader and self.doFooter:
                self.writeFooter()
            if self.header:
                self.writeHeader(self.header)
            self.prevHeader = self.header
        if message: self.writeMessage(message)

    #--Abstract/null writing functions...
    def writeHeader(self,header):
        """Write header. Abstract/null version."""
        pass
    def writeFooter(self):
        """Write mess. Abstract/null version."""
        pass
    def writeMessage(self,message):
        """Write message to log. Abstract/null version."""
        pass


class LogFile(Log):
    """Log that writes messages to file."""
    def __init__(self,out):
        self.out = out
        Log.__init__(self)

    def writeHeader(self,header):
        self.out.write(header+'\n')

    def writeFooter(self):
        self.out.write('\n')

    def writeMessage(self,message):
        self.out.write(message+'\n')


def deprint(*args,**keyargs):
    """Prints message along with file and line location."""
    if not conf.deprintOn and not keyargs.get('on'): return

    import inspect
    stack = inspect.stack()
    file,line,function = stack[1][1:4]
    msg = '%s %4d %s: %s' % (GPath(file).tail.s,line,function,' '.join(map(str,args)))

    if keyargs.get('traceback',False):
        import traceback, cStringIO
        o = cStringIO.StringIO()
        o.write(msg+'\n')
        traceback.print_exc(file=o)
        msg = o.getvalue()
        o.close()
    print msg

def delist(header,items,on=False):
    """Prints list as header plus items."""
    if not conf.deprintOn and not on: return
    import inspect
    stack = inspect.stack()
    file,line,function = stack[1][1:4]
    print '%s %4d %s: %s' % (GPath(file).tail.s,line,function,str(header))
    if items == None:
        print '> None'
    else:
        for indexItem in enumerate(items): print '>%2d: %s' % indexItem

