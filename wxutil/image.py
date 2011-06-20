import wx

from ..util import GPath

# Images ----------------------------------------------------------------------
images = {} #--global for collection of images.

#------------------------------------------------------------------------------
class Image:
    """Wrapper for images, allowing access in various formats/classes.

    Allows image to be specified before wx.App is initialized."""
    def __init__(self,file,type=wx.BITMAP_TYPE_ANY ):
        self.file = GPath(file)
        self.type = type
        self.bitmap = None
        self.icon = None
        if not GPath(self.file).exists():
            raise wryebase.error.ArgumentError(_("Missing resource file: %s.") % (self.file,))

    def GetBitmap(self):
        if not self.bitmap:
            self.bitmap = wx.Bitmap(self.file.s,self.type)
        return self.bitmap

    def GetIcon(self):
        if not self.icon:
            self.icon = wx.EmptyIcon()
            self.icon.CopyFromBitmap(self.GetBitmap())
        return self.icon

#------------------------------------------------------------------------------
class ImageBundle:
    """Wrapper for bundle of images.

    Allows image bundle to be specified before wx.App is initialized."""
    def __init__(self):
        self.images = []
        self.iconBundle = None

    def Add(self,image):
        self.images.append(image)

    def GetIconBundle(self):
        if not self.iconBundle:
            self.iconBundle = wx.IconBundle()
            for image in self.images:
                self.iconBundle.AddIcon(image.GetIcon())
        return self.iconBundle

#------------------------------------------------------------------------------
class ImageList:
    """Wrapper for wx.ImageList.

    Allows ImageList to be specified before wx.App is initialized.
    Provides access to ImageList integers through imageList[key]."""
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.data = []
        self.indices = {}
        self.imageList = None

    def Add(self,image,key):
        self.data.append((key,image))

    def GetImageList(self):
        if not self.imageList:
            indices = self.indices
            imageList = self.imageList = wx.ImageList(self.width,self.height)
            for key,image in self.data:
                indices[key] = imageList.Add(image.GetBitmap())
        return self.imageList

    def __getitem__(self,key):
        self.GetImageList()
        return self.indices[key]

