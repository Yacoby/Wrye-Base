import string

import wx

from ..import wtex
from ..localization import _
from ..util import GPath, Path, getStringBuffer

from sizer import spacer, hSizer, vSizer
from common import button, bitmapButton, staticText, checkBox
#from balt import  button, colors, wx.ID_ANY, defPos, staticText, bitmapButton

#------------------------------------------------------------------------------
#I don't have a clue what this does. This was in bosh, but only used here
gQuestion = False 

# Modal Dialogs ---------------------------------------------------------------
#------------------------------------------------------------------------------
def askDirectory(parent,message=_('Choose a directory.'),defaultPath=''):
    """Shows a modal directory dialog and return the resulting path, or None if canceled."""
    dialog = wx.DirDialog(parent,message,GPath(defaultPath).s,style=wx.DD_NEW_DIR_BUTTON)
    if dialog.ShowModal() != wx.ID_OK:
        dialog.Destroy()
        return None
    else:
        path = GPath(dialog.GetPath())
        dialog.Destroy()
        return path

#------------------------------------------------------------------------------
def askContinue(parent,settings,message,continueKey,title=_('Warning')):
    """Shows a modal continue query if value of continueKey is false. Returns True to continue.
    Also provides checkbox "Don't show this in future." to set continueKey to true."""
    #--ContinueKey set?
    if settings.get(continueKey):
        return wx.ID_OK
    #--Generate/show dialog
    dialog = wx.Dialog(parent,wx.ID_ANY,title,size=(350,200),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
    icon = wx.StaticBitmap(dialog,wx.ID_ANY,
        wx.ArtProvider_GetBitmap(wx.ART_WARNING,wx.ART_MESSAGE_BOX, (32,32)))
    gCheckBox = checkBox(dialog,_("Don't show this in the future."))
    #--Layout
    sizer = vSizer(
        (hSizer(
            (icon,0,wx.ALL,6),
            (staticText(dialog,message,style=wx.ST_NO_AUTORESIZE),1,wx.EXPAND|wx.LEFT,6),
            ),1,wx.EXPAND|wx.ALL,6),
        (gCheckBox,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,6),
        (hSizer( #--Save/Cancel
            spacer,
            button(dialog,id=wx.ID_OK),
            (button(dialog,id=wx.ID_CANCEL),0,wx.LEFT,4),
            ),0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,6),
        )
    dialog.SetSizer(sizer)
    #--Get continue key setting and return
    result = dialog.ShowModal()
    if gCheckBox.GetValue():
        settings[continueKey] = 1
    return result in (wx.ID_OK,wx.ID_YES)

def askContinueShortTerm(parent,message,title=_('Warning')):
    """Shows a modal continue query  Returns True to continue.
    Also provides checkbox "Don't show this in for rest of operation."."""
    #--Generate/show dialog
    dialog = wx.Dialog(parent,wx.ID_ANY,title,size=(350,200),
                       style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
    icon = wx.StaticBitmap(dialog,wx.ID_ANY,
                           wx.ArtProvider_GetBitmap(wx.ART_WARNING,
                                                    wx.ART_MESSAGE_BOX,
                                                    (32,32)
                                                    )
                           )
    gCheckBox = checkBox(dialog,_("Don't show this for rest of operation."))
    #--Layout
    sizer = vSizer(
        (hSizer(
            (icon,0,wx.ALL,6),
            (staticText(dialog,message,style=wx.ST_NO_AUTORESIZE),
                        1,wx.EXPAND|wx.LEFT,6
            ),
        ),1,wx.EXPAND|wx.ALL,6),
        (gCheckBox,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,6),
        (hSizer( #--Save/Cancel
            spacer,
            button(dialog,id=wx.ID_OK),
            (button(dialog,id=wx.ID_CANCEL),0,wx.LEFT,4),
            ),0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,6),
        )
    dialog.SetSizer(sizer)
    #--Get continue key setting and return
    result = dialog.ShowModal()
    if result in (wx.ID_OK,wx.ID_YES):
        if gCheckBox.GetValue():
            return 2
        return True
    return False

#------------------------------------------------------------------------------
def askOpen(parent, title='',defaultDir='',defaultFile='',
            wildcard='',style=wx.OPEN,mustExist=False):
    """Show as file dialog and return selected path(s)."""
    defaultDir,defaultFile = [GPath(x).s for x in (defaultDir,defaultFile)]
    dialog = wx.FileDialog(parent,title,defaultDir,defaultFile,wildcard, style)
    if dialog.ShowModal() != wx.ID_OK:
        result = False
    elif style & wx.MULTIPLE:
        result = map(GPath,dialog.GetPaths())
        if mustExist:
            for path in result:
                if not path.exists():
                    result = False
                    break
    else:
        result = GPath(dialog.GetPath())
        if mustExist and not result.exists():
            result = False
    dialog.Destroy()
    return result

def askOpenMulti(parent,title='',defaultDir='',
                 defaultFile='',wildcard='',style=wx.OPEN|wx.MULTIPLE):
    """Show as save dialog and return selected path(s)."""
    return askOpen(parent,title,defaultDir,defaultFile,wildcard,style )

def askSave(parent,title='',defaultDir='',defaultFile='',
            wildcard='',style=wx.OVERWRITE_PROMPT):
    """Show as save dialog and return selected path(s)."""
    return askOpen(parent,title,defaultDir,defaultFile,wildcard,wx.SAVE|style )

#------------------------------------------------------------------------------
def askText(parent,message,title='',default=''):
    """Shows a text entry dialog and returns result or None if canceled."""
    dialog = wx.TextEntryDialog(parent,message,title,default)
    if dialog.ShowModal() != wx.ID_OK:
        dialog.Destroy()
        return None
    else:
        value = dialog.GetValue()
        dialog.Destroy()
        return value

#------------------------------------------------------------------------------
def askNumber(parent,message,prompt='',title='',value=0,min=0,max=10000):
    """Shows a text entry dialog and returns result or None if canceled."""
    dialog = wx.NumberEntryDialog(parent,message,prompt,title,value,min,max)
    if dialog.ShowModal() != wx.ID_OK:
        dialog.Destroy()
        return None

    else:
        value = dialog.GetValue()
        dialog.Destroy()
        return value

# Message Dialogs -------------------------------------------------------------
def askStyled(parent,message,title,style):
    """Shows a modal MessageDialog.
    Use ErrorMessage, WarningMessage or InfoMessage."""
    dialog = wx.MessageDialog(parent,message,title,style)
    result = dialog.ShowModal()
    dialog.Destroy()
    return result in (wx.ID_OK,wx.ID_YES)

def askOk(parent,message,title=''):
    """Shows a modal error message."""
    return askStyled(parent,message,title,wx.OK|wx.CANCEL)

def askYes(parent,message,title='',default=True,icon=wx.ICON_EXCLAMATION):
    """Shows a modal warning or question message."""
    style = wx.YES_NO|icon|((wx.NO_DEFAULT,wx.YES_DEFAULT)[default])
    return askStyled(parent,message,title,style)

def askWarning(parent,message,title=_('Warning')):
    """Shows a modal warning message."""
    return askStyled(parent,message,title,wx.OK|wx.CANCEL|wx.ICON_EXCLAMATION)

def showOk(parent,message,title=''):
    """Shows a modal error message."""
    return askStyled(parent,message,title,wx.OK)

def showError(parent,message,title=_('Error')):
    """Shows a modal error message."""
    return askStyled(parent,message,title,wx.OK|wx.ICON_HAND)

def showWarning(parent,message,title=_('Warning')):
    """Shows a modal warning message."""
    return askStyled(parent,message,title,wx.OK|wx.ICON_EXCLAMATION)

def showInfo(parent,message,title=_('Information')):
    """Shows a modal information message."""
    return askStyled(parent,message,title,wx.OK|wx.ICON_INFORMATION)

def showList(parent,header,items,maxItems=0,title=''):
    """Formats a list of items into a message for use in a Message."""
    numItems = len(items)
    if maxItems <= 0: maxItems = numItems
    message = string.Template(header).substitute(count=numItems)
    message += '\n* '+'\n* '.join(items[:min(numItems,maxItems)])
    if numItems > maxItems:
        message += _('\n(And %d others.)') % (numItems - maxItems,)
    return askStyled(parent,message,title,wx.OK)

#------------------------------------------------------------------------------
def showLogClose(settings, evt=None):
    """Handle log message closing."""
    window = evt.GetEventObject()
    if not window.IsIconized() and not window.IsMaximized():
        settings['balt.LogMessage.pos'] = window.GetPositionTuple()
        settings['balt.LogMessage.size'] = window.GetSizeTuple()
    window.Destroy()

def showQuestionLogCloseYes(settings, event,window):
    """Handle log message closing."""
    if window:
        if not window.IsIconized() and not window.IsMaximized():
            settings['balt.LogMessage.pos'] = window.GetPositionTuple()
            settings['balt.LogMessage.size'] = window.GetSizeTuple()
        window.Destroy()
    gQuestion = True

def showQuestionLogCloseNo(settings, event, window):
    """Handle log message closing."""
    if window:
        if not window.IsIconized() and not window.IsMaximized():
            settings['balt.LogMessage.pos'] = window.GetPositionTuple()
            settings['balt.LogMessage.size'] = window.GetSizeTuple()
        window.Destroy()
    gQuestion = False

def showLog(parent,settings,logText,title='',style=0,
            asDialog=True,fixedFont=False,icons=None,size=True,question=False):
    """Display text in a log window"""
    #--Sizing
    pos = settings.get('balt.LogMessage.pos',wx.DefaultPosition)
    if size:
        size = settings.get('balt.LogMessage.size',(400,400))
    #--Dialog or Frame
    if asDialog:
        window = wx.Dialog(parent,wx.ID_ANY,title,pos=pos,size=size,
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
    else:
        window = wx.Frame(parent,wx.ID_ANY,title,pos=pos,size=size,
            style= (wx.RESIZE_BORDER | wx.CAPTION | wx.SYSTEM_MENU | wx.CLOSE_BOX | wx.CLIP_CHILDREN))
        if icons: window.SetIcons(icons)
    window.SetSizeHints(200,200)
    window.Bind(wx.EVT_CLOSE, lambda *a: showLogClose(settings, *a))
    window.SetBackgroundColour(wx.NullColour) #--Bug workaround to ensure that default colour is being used.
    #--Text
    textCtrl = wx.TextCtrl(window,wx.ID_ANY,logText,style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH2|wx.SUNKEN_BORDER  )
    if fixedFont:
        fixedFont = wx.SystemSettings_GetFont(wx.SYS_ANSI_FIXED_FONT )
        fixedFont.SetPointSize(8)
        fixedStyle = wx.TextAttr()
        #fixedStyle.SetFlags(0x4|0x80)
        fixedStyle.SetFont(fixedFont)
        textCtrl.SetStyle(0,textCtrl.GetLastPosition(),fixedStyle)
    if question:
        gQuestion = False
        #--Buttons
        gYesButton = button(window,id=wx.ID_YES)
        gYesButton.Bind(wx.EVT_BUTTON, lambda evt, temp=window: showQuestionLogCloseYes(evt, temp) )
        gYesButton.SetDefault()
        gNoButton = button(window,id=wx.ID_NO)
        gNoButton.Bind(wx.EVT_BUTTON, lambda evt, temp=window: showQuestionLogCloseNo(evt, temp) )
        #--Layout
        window.SetSizer(
            vSizer(
                (textCtrl,1,wx.EXPAND|wx.ALL^wx.BOTTOM,2),
                hSizer((gYesButton,0,wx.ALIGN_RIGHT|wx.ALL,4),
                    (gNoButton,0,wx.ALIGN_RIGHT|wx.ALL,4))
                )
            )
    else:
        #--Buttons
        gOkButton = button(window,id=wx.ID_OK,onClick=lambda event: window.Close())
        gOkButton.SetDefault()
        #--Layout
        window.SetSizer(
            vSizer(
                (textCtrl,1,wx.EXPAND|wx.ALL^wx.BOTTOM,2),
                (gOkButton,0,wx.ALIGN_RIGHT|wx.ALL,4),
                )
            )
    #--Show
    if asDialog:
        window.ShowModal()
        window.Destroy()
    else:
        window.Show()
    return gQuestion

#------------------------------------------------------------------------------
def showWryeLog(parent,settings,logText,title='',
                style=0,asDialog=True,icons=None):
    """Convert logText from wtxt to html and display. Optionally, logText can be path to an html file."""
    try:
        import wx.lib.iewin
    except ImportError:
        # Comtypes not available most likely! so do it this way:
        import os
        if not isinstance(logText, Path):
            logPath = settings.get('balt.WryeLog.temp',
                                    Path.getcwd().join('WryeLogTemp.html'))
            cssDir = settings.get('balt.WryeLog.cssDir', GPath(''))
            ins = getStringBuffer(logText+'\n{{CSS:wtxt_sand_small.css}}')
            out = logPath.open('w')
            wtex.WryeText.genHtml(ins,out,cssDir)
            out.close()
            logText = logPath
        os.startfile(logText.s)
        return

    #--Sizing
    pos = settings.get('balt.WryeLog.pos', wx.DefaultPosition)
    size = settings.get('balt.WryeLog.size',(400,400))
    #--Dialog or Frame
    if asDialog:
        window = wx.Dialog(parent,wx.ID_ANY,title,pos=pos,size=size,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
    else:
        window = wx.Frame(parent,wx.ID_ANY,title,pos=pos,size=size,
            style= (wx.RESIZE_BORDER | wx.CAPTION | wx.SYSTEM_MENU | wx.CLOSE_BOX | wx.CLIP_CHILDREN))
        if icons: window.SetIcons(icons)
    window.SetSizeHints(200,200)
    window.Bind(wx.EVT_CLOSE, lambda *a: showLogClose(settings, *a))
    #--Text
    textCtrl = wx.lib.iewin.IEHtmlWindow(window, wx.ID_ANY, style = wx.NO_FULL_REPAINT_ON_RESIZE)
    if not isinstance(logText, Path):
        logPath = settings.get('balt.WryeLog.temp', Path.getcwd().join('WryeLogTemp.html'))
        cssDir = settings.get('balt.WryeLog.cssDir', GPath(''))
        ins = getStringBuffer(logText+'\n{{CSS:wtxt_sand_small.css}}')
        out = logPath.open('w')
        wtex.WryeText.genHtml(ins,out,cssDir)
        out.close()
        logText = logPath
    textCtrl.Navigate(logText.s,0x2) #--0x2: Clear History
    #--Buttons
    bitmap = wx.ArtProvider_GetBitmap(wx.ART_GO_BACK,wx.ART_HELP_BROWSER, (16,16))
    gBackButton = bitmapButton(window,bitmap,onClick=lambda evt: textCtrl.GoBack())
    bitmap = wx.ArtProvider_GetBitmap(wx.ART_GO_FORWARD,wx.ART_HELP_BROWSER, (16,16))
    gForwardButton = bitmapButton(window,bitmap,onClick=lambda evt: textCtrl.GoForward())
    gOkButton = button(window,id=wx.ID_OK,onClick=lambda event: window.Close())
    gOkButton.SetDefault()
    if not asDialog:
        window.SetBackgroundColour(gOkButton.GetBackgroundColour())
    #--Layout
    window.SetSizer(
        vSizer(
            (textCtrl,1,wx.EXPAND|wx.ALL^wx.BOTTOM,2),
            (hSizer(
                gBackButton,
                gForwardButton,
                spacer,
                gOkButton,
                ),0,wx.ALL|wx.EXPAND,4),
            )
        )
    #--Show
    if asDialog:
        window.ShowModal()
        if window:
            settings['balt.WryeLog.pos'] = window.GetPositionTuple()
            settings['balt.WryeLog.size'] = window.GetSizeTuple()
            window.Destroy()
    else:
        window.Show()

