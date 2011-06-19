import wx
import textwrap

# Elements --------------------------------------------------------------------
def bell(arg=None):
    """"Rings the system bell and returns the input argument (useful for return bell(value))."""
    wx.Bell()
    return arg

def tooltip(text,wrap=50):
    """Returns tooltip with wrapped copy of text."""
    text = textwrap.fill(text,wrap)
    return wx.ToolTip(text)

class textCtrl(wx.TextCtrl):
    """wx.TextCtrl with automatic tooltip if text goes past the width of the control."""
    def __init__(self, parent, id=wx.ID_ANY, name='', size=wx.DefaultSize, style=0, autotooltip=True):
        wx.TextCtrl.__init__(self,parent,id,name,size=size,style=style)
        if autotooltip:
            self.Bind(wx.EVT_TEXT, self.OnTextChange)
            self.Bind(wx.EVT_SIZE, self.OnSizeChange)

    def UpdateToolTip(self, text):
        if self.GetClientSize()[0] < self.GetTextExtent(text)[0]:
            self.SetToolTip(tooltip(text))
        else:
            self.SetToolTip(tooltip(''))

    def OnTextChange(self,event):
        self.UpdateToolTip(event.GetString())
        event.Skip()
    def OnSizeChange(self, event):
        self.UpdateToolTip(self.GetValue())
        event.Skip()

class comboBox(wx.ComboBox):
    """wx.ComboBox with automatic tooltipi if text is wider than width of control."""
    def __init__(self, *args, **kwdargs):
        autotooltip = kwdargs.get('autotooltip',True)
        if 'autotooltip' in kwdargs:
            del kwdargs['autotooltip']
        wx.ComboBox.__init__(self, *args, **kwdargs)
        if autotooltip:
            self.Bind(wx.EVT_SIZE, self.OnChange)
            self.Bind(wx.EVT_TEXT, self.OnChange)

    def OnChange(self, event):
        if self.GetClientSize()[0] < self.GetTextExtent(self.GetValue())[0]+30:
            self.SetToolTip(tooltip(self.GetValue()))
        else:
            self.SetToolTip(tooltip(''))
        event.Skip()

def bitmapButton(parent,bitmap,pos=wx.DefaultPosition,size=wx.DefaultSize,style=wx.BU_AUTODRAW,val=wx.DefaultValidator,
        name='button',id=wx.ID_ANY,onClick=None,tip=None,onRClick=None):
    """Creates a button, binds click function, then returns bound button."""
    gButton = wx.BitmapButton(parent,id,bitmap,pos,size,style,val,name)
    if onClick: gButton.Bind(wx.EVT_BUTTON,onClick)
    if onRClick: gButton.Bind(wx.EVT_RIGHT_DOWN,onRClick)
    if tip: gButton.SetToolTip(tooltip(tip))
    return gButton

def button(parent,label='',pos=wx.DefaultPosition,size=wx.DefaultSize,style=0,val=wx.DefaultValidator,
        name='button',id=wx.ID_ANY,onClick=None,tip=None):
    """Creates a button, binds click function, then returns bound button."""
    gButton = wx.Button(parent,id,label,pos,size,style,val,name)
    if onClick: gButton.Bind(wx.EVT_BUTTON,onClick)
    if tip: gButton.SetToolTip(tooltip(tip))
    return gButton

def toggleButton(parent,label='',pos=wx.DefaultPosition,size=wx.DefaultSize,style=0,val=wx.DefaultValidator,
        name='button',id=wx.ID_ANY,onClick=None,tip=None):
    """Creates a toggle button, binds toggle function, then returns bound button."""
    gButton = wx.ToggleButton(parent,id,label,pos,size,style,val,name)
    if onClick: gButton.Bind(wx.EVT_TOGGLEBUTTON,onClick)
    if tip: gButton.SetToolTip(tooltip(tip))
    return gButton

def checkBox(parent,label='',pos=wx.DefaultPosition,size=wx.DefaultSize,style=0,val=wx.DefaultValidator,
        name='checkBox',id=wx.ID_ANY,onCheck=None,tip=None):
    """Creates a checkBox, binds check function, then returns bound button."""
    gCheckBox = wx.CheckBox(parent,id,label,pos,size,style,val,name)
    if onCheck: gCheckBox.Bind(wx.EVT_CHECKBOX,onCheck)
    if tip: gCheckBox.SetToolTip(tooltip(tip))
    return gCheckBox

def staticText(parent,label='',pos=wx.DefaultPosition,size=wx.DefaultSize,style=0,name="staticText",id=wx.ID_ANY,):
    """Static text element."""
    return wx.StaticText(parent,id,label,pos,size,style,name)

def spinCtrl(parent,value='',pos=wx.DefaultPosition,size=wx.DefaultSize,style=wx.SP_ARROW_KEYS,
        min=0,max=100,initial=0,name='wxSpinctrl',id=wx.ID_ANY,onSpin=None,tip=None):
    """Spin control with event and tip setting."""
    gSpinCtrl=wx.SpinCtrl(parent,id,value,pos,size,style,min,max,initial,name)
    if onSpin: gSpinCtrl.Bind(wx.EVT_SPINCTRL,onSpin)
    if tip: gSpinCtrl.SetToolTip(tooltip(tip))
    return gSpinCtrl

# Sub-Windows -----------------------------------------------------------------
def leftSash(parent,defaultSize=(100,100),onSashDrag=None):
    """Creates a left sash window."""
    sash = wx.SashLayoutWindow(parent,style=wx.SW_3D)
    sash.SetDefaultSize(defaultSize)
    sash.SetOrientation(wx.LAYOUT_VERTICAL)
    sash.SetAlignment(wx.LAYOUT_LEFT)
    sash.SetSashVisible(wx.SASH_RIGHT, True)
    if onSashDrag:
        id = sash.GetId()
        sash.Bind(wx.EVT_SASH_DRAGGED_RANGE, onSashDrag,id=id,id2=id)
    return sash

def topSash(parent,defaultSize=(100,100),onSashDrag=None):
    """Creates a top sash window."""
    sash = wx.SashLayoutWindow(parent,style=wx.SW_3D)
    sash.SetDefaultSize(defaultSize)
    sash.SetOrientation(wx.LAYOUT_HORIZONTAL)
    sash.SetAlignment(wx.LAYOUT_TOP)
    sash.SetSashVisible(wx.SASH_BOTTOM, True)
    if onSashDrag:
        id = sash.GetId()
        sash.Bind(wx.EVT_SASH_DRAGGED_RANGE, onSashDrag,id=id,id2=id)
    return sash

