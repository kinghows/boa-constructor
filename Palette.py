#----------------------------------------------------------------------
# Name:        Palette.py
# Purpose:     Main frame containing palette for visual frame design
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:Frame:BoaFrame

print 'importing Palette'

import os

from wxPython.wx import *

import PaletteMapping
import sender
import Help, Preferences, Utils

from Preferences import IS, toPyPath, flatTools

from ExternalLib.buttons import wxGenButton, wxGenBitmapButton, wxGenToggleButton, wxGenBitmapToggleButton, wxGenButtonEvent

currentMouseOverTip = ''

wxEVT_CREATE_NEW = wxNewId()

def EVT_CREATE_NEW(win, func):
    win.Connect(-1, -1, wxEVT_CREATE_NEW, func)

class CreateNewEvent(wxPyEvent):
    def __init__(self, name, controller):
        wxPyEvent.__init__(self)
        self.SetEventType(wxEVT_CREATE_NEW)
        self.name = name
        self.controller = controller

[wxID_BOAFRAME, wxID_BOAFRAMECONTEXTHELPSEARCH, wxID_BOAFRAMEPALETTE, wxID_BOAFRAMETOOLBAR] = map(lambda _init_ctrls: wxNewId(), range(4))

[wxID_BOAFRAMETOOLBARTOOLS0, wxID_BOAFRAMETOOLBARTOOLS1, wxID_BOAFRAMETOOLBARTOOLS2] = map(lambda _init_coll_toolBar_Tools: wxNewId(), range(3))

class BoaFrame(wxFrame, Utils.FrameRestorerMixin):
    def _init_coll_toolBar_Tools(self, parent):

        parent.AddTool(bitmap = IS.load('Images/Shared/Inspector.png'), id = wxID_BOAFRAMETOOLBARTOOLS0, isToggle = false, longHelpString = '', pushedBitmap = wxNullBitmap, shortHelpString = 'Brings the Inspector to the front')
        parent.AddTool(bitmap = IS.load('Images/Shared/Editor.png'), id = wxID_BOAFRAMETOOLBARTOOLS1, isToggle = false, longHelpString = '', pushedBitmap = wxNullBitmap, shortHelpString = 'Brings the Editor to the front')
        parent.AddTool(bitmap = IS.load('Images/Shared/ClassBrowser.png'), id = wxID_BOAFRAMETOOLBARTOOLS2, isToggle = false, longHelpString = '', pushedBitmap = wxNullBitmap, shortHelpString = 'Opens the Class explorer for wxPython')
        EVT_TOOL(self, wxID_BOAFRAMETOOLBARTOOLS0, self.OnInspectorToolClick)
        EVT_TOOL(self, wxID_BOAFRAMETOOLBARTOOLS1, self.OnEditorToolClick)
        EVT_TOOL(self, wxID_BOAFRAMETOOLBARTOOLS2, self.OnExplorerToolClick)

        parent.Realize()

    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, id = wxID_BOAFRAME, name = '', parent = prnt, pos = wxPoint(116, 275), size = wxSize(645, 74), style = wxDEFAULT_FRAME_STYLE, title = 'Boa Constructor - Python IDE & wxPython GUI Builder')
        self._init_utils()
        EVT_CLOSE(self, self.OnCloseWindow)
        EVT_ICONIZE(self, self.OnBoaframeIconize)

        self.toolBar = wxToolBar(id = wxID_BOAFRAMETOOLBAR, name = 'toolBar', parent = self, pos = wxPoint(0, -28), size = wxSize(637, 28), style = wxTB_HORIZONTAL | wxNO_BORDER | Preferences.flatTools)
        self._init_coll_toolBar_Tools(self.toolBar)
        self.SetToolBar(self.toolBar)

        self.palette = wxNotebook(id = wxID_BOAFRAMEPALETTE, name = 'palette', parent = self, pos = wxPoint(0, 0), size = wxSize(637, 19), style = 0)

        self.contextHelpSearch = wxTextCtrl(id = wxID_BOAFRAMECONTEXTHELPSEARCH, name = 'contextHelpSearch', parent = self.toolBar, pos = wxPoint(232, 0), size = wxSize(100, 21), style = 0, value = '')
        EVT_TEXT_ENTER(self.contextHelpSearch, wxID_BOAFRAMECONTEXTHELPSEARCH, self.OnSearchEnter)
        EVT_SET_FOCUS(self.contextHelpSearch, self.OnHelpSearchFocus)

    def __init__(self, parent, id, app):
        self._init_ctrls(parent)

        self.winConfOption = 'palette'
        self.loadDims()

        self.SetBackgroundColour(wxSystemSettings_GetSystemColour(wxSYS_COLOUR_BTNFACE))

        self.paletteStyle = Preferences.paletteStyle
        if self.paletteStyle == 'menu':
            self.menuBar = wxMenuBar()
            self.SetMenuBar(self.menuBar)
            self.palette.Show(false)

        self.app = app
        self.destroying = false

        self.widgetSet = {}
        self.SetIcon(IS.load('Images/Icons/Boa.ico'))

        self.browser = None

        self.toolBar.AddSeparator()

        self.componentSB = ComponentSelection(self)

        self.toolBar.AddSeparator()
        self.addTool('Images/Shared/CustomHelp', 'Test', 'Test', self.OnTest)

        # Add main helpbuttons defined in the config file
        conf = Utils.createAndReadConfig('Explorer')
        self.paletteHelpItems = eval(conf.get('help', 'palettehelp'))

        self.toolBar.AddSeparator()
        self.addTool('Images/Shared/Help', 'Boa or selected component help',
              'Show help', self.OnHelpToolClick)
        self.addTool('Images/Shared/wxWinHelp', 'wxPython help',
              'Show help', self.OnWxWinHelpToolClick)
        self.addTool('Images/Shared/PythonHelp', 'Python help',
              'Show help', self.OnPythonHelpToolClick)

        # Add additional helpbuttons if defined in the config file
        customHelpItems = eval(conf.get('help', 'customhelp'))
        self.customHelpItems = {}
        for caption, helpFile in customHelpItems.items():
            mID = wxNewId()
            self.toolBar.AddTool(mID, IS.load('Images/Shared/CustomHelp.png'),
              shortHelpString = caption)
            EVT_TOOL(self, mID, self.OnCustomHelpToolClick)
            self.customHelpItems[mID] = (caption, helpFile)

        self.toolBar.AddControl(self.contextHelpSearch)

        if wxPlatform == '__WXGTK__':
            self.toolBar.AddSeparator()
            self.addTool('Images/Shared/CloseWindow', 'Exit', '', self.OnCloseClick)
        self.toolBar.AddSeparator()
        self.toolBar.Realize()

        self.palettePages = []
        self.senders = sender.SenderMapper()

        EVT_CREATE_NEW(self, self.OnCreateNew)

    def initPalette(self, inspector, editor):
        self.inspector = inspector
        self.editor = editor

        transpSF = ''
        if Preferences.paletteStyle == 'menu':
            mb = self.menuBar
        else:
            mb = None

        # XXX Set these from class
        if not hasattr(sys, 'cyclops'):
            # 'New' page
            palettePage = NewPalettePage(self.palette, 'New', 
                  'Images/Palette/'+transpSF, self, self.widgetSet, 
                  self.senders, self)

            for modelName in PaletteMapping.PaletteStore.paletteLists['New']:
                palettePage.addButton2(modelName,
                    PaletteMapping.PaletteStore.newControllers[modelName],
                    wxGenBitmapButton)
            if mb: mb.Append(menu = palettePage.menu, title = 'New')
            self.palettePages.append(palettePage)
            # Normal control pages
            for palette in PaletteMapping.palette:
                palettePage = PalettePage(self.palette, palette[0], 
                      'Images/Palette/'+transpSF, self, self.widgetSet, 
                      self.senders, self.componentSB, self)
                palettePage.addToggleBitmaps(palette[2], None, None)
                self.palettePages.append(palettePage)
                if mb: mb.Append(menu = palettePage.menu, title = palette[0])
            # Dialog page
            if PaletteMapping.dialogPalette[2]:
                self.dialogPalettePage = PanelPalettePage(self.palette, 
                      PaletteMapping.dialogPalette[0], 
                      'Images/Palette/'+transpSF, self, self.widgetSet, 
                      self.senders, self.componentSB, self)
                for dialog in PaletteMapping.dialogPalette[2]:
                    self.dialogPalettePage.addButton(
                          PaletteMapping.compInfo[dialog][0],
                          dialog, PaletteMapping.compInfo[dialog][1],
                          self.OnDialogPaletteClick, None, None, 
                          wxGenBitmapButton)
                self.palettePages.append(self.dialogPalettePage)
                if mb: 
                    mb.Append(menu = self.dialogPalettePage.menu, title = 'Dialogs')
            # Zope page
            conf = Utils.createAndReadConfig('Explorer')
            if conf.has_option('explorer', 'zope'):
                self.zopePalettePage = ZopePalettePage(self.palette, 
                      PaletteMapping.zopePalette[0], 'Images/Palette/'+transpSF, 
                      self, self.widgetSet, self.senders, self.componentSB, self)
                self.zopePalettePage.addToggleBitmaps(
                      PaletteMapping.zopePalette[2], None, None)
                self.palettePages.append(self.zopePalettePage)
                if mb: mb.Append(menu = self.zopePalettePage.menu, title = 'Zope')
        else:
            palettePage = None

        # Prototype for composites
        # Composites are very much not thought out right now, but basically
        # reflects Frames in Delphi 5. A D5 frame is a composite component
        # for reuse of common control combinations. In implementation it's
        # very much like Delphi's form inheritance, i.e. by changing the parent
        # all children will be updated.
        # Current thoughts on implementation in Boa:
        #    To centralise, I like the idea of storing initialisations in a
        #    sepatate file and using 'import' to load controls into a frame.

##        self.composites = CompositeListCtrlPalPage(self.palette, -1, style = wxLC_SMALL_ICON)
##        self.palette.AddPage(self.composites, 'Composites')
##        self.composites.InsertStringItem(0, 'OK / Cancel buttons')
##        self.composites.InsertStringItem(0, 'Tabbed dialog')
##        self.composites.InsertStringItem(0, 'Name/Value')
##        self.composites.Enable(false)

        # Prototype for templates
        # Templates is a real simple idea, instead of starting from a blank
        # frame, start from a previously saved frame in the templates directory

##        self.templates = TemplateListCtrlPalPage(self.palette, -1, style = wxLC_SMALL_ICON)
##        self.palette.AddPage(self.templates, 'Templates')
##        self.templates.InsertStringItem(0, 'Menu/Toolbar/StatusBar')
##        self.templates.InsertStringItem(0, 'Wizard')
##        self.templates.Enable(false)

    def setDefaultDimensions(self):
        self.SetDimensions(0, 0,
            Preferences.screenWidth - Preferences.windowManagerSide * 2,
            Preferences.paletteHeight)

    def addTool(self, filename, text, help, func, toggle = false):
        mID = wxNewId()
        self.toolBar.AddTool(mID, IS.load(filename+'.png'),
          shortHelpString = text, isToggle = toggle)
        EVT_TOOL(self, mID, func)
        return mID

    def OnInspectorToolClick(self, event):
        self.inspector.restore()

    def OnEditorToolClick(self, event):
        self.editor.restore()

    def OnHelpToolClick(self, event):
        if self.componentSB.selection:
            Help.showCtrlHelp(self.componentSB.selection[1].__name__)
        else:
            Help.showMainHelp(self.paletteHelpItems['boa'])

    def OnWxWinHelpToolClick(self, event):
        Help.showMainHelp(self.paletteHelpItems['wx'])

    def OnPythonHelpToolClick(self, event):
        Help.showMainHelp(self.paletteHelpItems['python'])

    def OnCustomHelpToolClick(self, event):
        caption, helpFile = self.customHelpItems[event.GetId()]
        Help.showHelp(helpFile)

    def OnFileExit(self, event):
        self.Close()

    def OnDialogPaletteClick(self, event):
        cls, cmp = self.dialogPalettePage.widgets[`event.GetId()`][1:]
        self.editor.addNewDialog(cls, cmp)

    def OnZopePaletteClick(self, event):
        cls, cmp = self.zopePalettePage.widgets[`event.GetId()`][1:]

    def OnExplorerToolClick(self, event):
        if not self.browser:
            import ClassBrowser

            wxBeginBusyCursor()
            try:
                self.browser = ClassBrowser.ClassBrowserFrame(self)
            finally:
                wxEndBusyCursor()
        self.browser.restore()

    def OnComposeClick(self, event):
        pass
    def OnInheritClick(self, event):
        pass

    def OnCloseClick(self, event):
        self.Close()

    def OnCloseWindow(self, event):
        self.destroying = true
        try:
            if hasattr(self, 'editor') and self.editor:
                self.editor.destroying = true
                self.editor.Close()
                if not self.destroying:
                    return

            if hasattr(self, 'inspector'):
                self.inspector.destroying = true
                self.inspector.Close()

                if hasattr(self, 'app'):
                    self.app = None

            Help.delHelp()

            self.palette.Hide()
            for page in self.palettePages:
                page.destroy()

        finally:
            if not self.destroying:
                self.editor.destroying = false
                self.inspector.destroying = false
            else:
                self.Destroy()
                event.Skip()

    def OnUncheckComponent(self, event):
        self.componentSB.selectNone()

    def OnSearchEnter(self, event):
        Help.showContextHelp(self.contextHelpSearch.GetValue())
        event.Skip()

    def OnTest(self, event):
        import Tests
        Tests.test_wxFrame(self)

    def OnHelpSearchFocus(self, event):
        self.contextHelpSearch.SetSelection(0,
              len(self.contextHelpSearch.GetValue()))
        event.Skip()

    def OnCreateNew(self, event):
        self.editor.addNewPage(event.name, event.controller)
        event.Skip()

    def Iconize(self, iconize):
        if Help._hc:
            frm = Help._hc.GetFrame()
            if frm: frm.Iconize(iconize)
        wxFrame.Iconize(self, iconize)

    def OnBoaframeIconize(self, event):
        self.SetFocus()
        if Help._hc:
            frm = Help._hc.GetFrame()
            if frm: frm.Iconize(true)
        event.Skip()

class ComponentSelection:
    """ Controls the selection of the palette and access to associated
        palette mapping structures. Accessed by the Designer """
    def __init__(self, palette):
        wID = wxNewId()
        self.selComp = wxCheckBox(palette.toolBar, wID, '  (Nothing selected)', size = wxSize(120, 20))
        self.selComp.Enable(false)
        EVT_CHECKBOX(self.selComp, wID, palette.OnUncheckComponent)
        palette.toolBar.AddControl(self.selComp)

        cId = palette.addTool('Images/Shared/Compose', 'Compose', ' ', palette.OnComposeClick, toggle = true)
        iId = palette.addTool('Images/Shared/Inherit', 'Inherit', ' ', palette.OnInheritClick, toggle = true)
        palette.toolBar.ToggleTool(cId, true)
#        palette.toolBar.EnableTool(iId, false)

        self.selection = None
        self.prevPage = None

    def selectComponent(self, page, detail):
        if self.prevPage: self.prevPage.selectNone()
        self.selection = detail
        self.prevPage = page
        self.selComp.Enable(true)
        self.selComp.SetLabel('  '+detail[0])
        self.selComp.SetValue(true)

    def selectNone(self):
        if self.prevPage: self.prevPage.selectNone()
        self.selection = None
        self.selComp.Enable(false)
        self.selComp.SetLabel('  (Nothing selected)')
        self.selComp.SetValue(false)

class BasePalettePage:
    pass
class ListCtrlPalettePage(wxListCtrl, BasePalettePage):
    pass
class CompositeListCtrlPalPage(ListCtrlPalettePage):
    pass
class TemplateListCtrlPalPage(ListCtrlPalettePage):
    pass

class PanelPalettePage(wxPanel, BasePalettePage):
    defX = 5
    defY = 3
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, components, palette):
        wxPanel.__init__(self, parent, -1)

        self.palette = palette
        self.components = components
        self.senders = senders
        self.name = name
        self.bitmapPath = bitmapPath
        self.posX = self.defX
        self.posY = self.defY
        self.widgets = widgets
        self.buttons = {}
        parent.AddPage(self, name)
        self.eventOwner = eventOwner
        self.menu = wxMenu()
        self.menusCheckable = false

    def destroy(self):
        del self.senders
        del self.widgets
        self.DestroyChildren()
        for btn in self.buttons.values():
            btn.faceDnClr = None
            btn.shadowPen = None
            btn.highlightPen = None
            btn.focusIndPen = None
            btn.bmpLabel = None
        if self.palette.paletteStyle == 'tabs':
            self.menu.Destroy()

    def addButton(self, widgetName, wxClass, constrClass, clickEvt, hintFunc, hintLeaveFunc, btnType):
        mID = wxNewId()

        self.menu.Append(mID, widgetName, checkable=self.menusCheckable)
        EVT_MENU(self.palette, mID, clickEvt)

        self.widgets[`mID`] = (widgetName, wxClass, constrClass)

        if self.palette.paletteStyle == 'menu':
            return mID

        bmp = self.getButtonBmp(widgetName, wxClass)
        width = bmp.GetWidth() + 7
        height = bmp.GetHeight() + 7

        newButton = btnType(self, mID, None, wxPoint(self.posX, self.posY),
                           wxSize(width, height))

        newButton.SetBezelWidth(1)
        newButton.SetUseFocusIndicator(0)
        newButton.SetToolTipString(widgetName)
        newButton.SetBitmapLabel(bmp)

        EVT_BUTTON(self, mID, clickEvt)

        self.senders.addObject(newButton)
        self.buttons[widgetName] = newButton
        self.posX = self.posX + bmp.GetWidth() + 11

        return mID

    def getButtonBmp(self, name, wxClass):
        return PaletteMapping.bitmapForComponent(wxClass)

class NewPalettePage(PanelPalettePage):
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, palette):
        PanelPalettePage.__init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, palette, palette)
        self.selection = None

    def destroy(self):
        PanelPalettePage.destroy(self)

    def addButton(self, widgetName, wxClass, constrClass, clickEvt, hintFunc, hintLeaveFunc, btnType):
        mID = PanelPalettePage.addButton(self, widgetName, wxClass, constrClass, clickEvt, hintFunc, hintLeaveFunc, btnType)
        return mID

    def addButton2(self, name, Controller, btnType):
        mID = PanelPalettePage.addButton(self, name, Controller, None, self.OnClickTrap, None, None, btnType)
        EVT_MENU(self.palette.editor, mID, self.OnClickTrap)

        return mID

    def getButtonBmp(self, name, wxClass):
        return IS.load('%s%s.png' %(self.bitmapPath, name))

    def OnClickTrap(self, event):
        modPageInfo = self.widgets[`event.GetId()`]
        wxPostEvent(self.palette, CreateNewEvent(modPageInfo[0], modPageInfo[1]))

class PalettePage(PanelPalettePage):
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, components, palette):
        PanelPalettePage.__init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, components, palette)
        self.clickEvt = None
        self.selection = None
        self.menusCheckable = true

    def addToggleBitmaps(self, classes, hintFunc, hintLeaveFunc):
        for wxClass in classes:
            ci = PaletteMapping.compInfo[wxClass]
            self.addButton(ci[0], wxClass, ci[1], self.OnClickTrap, hintFunc, hintLeaveFunc, wxGenBitmapToggleButton)

    def OnClickTrap(self, event):
        wId = event.GetId()
        if self.palette.paletteStyle == 'tabs':
            obj = self.senders.getBtnObject(event)
            if obj.up:
                self.selectNone()
                self.components.selectNone()
            else:
                self.components.selectComponent(self, self.widgets[`wId`])
                self.selection = obj
        elif self.palette.paletteStyle == 'menu':
            sel = self.menu.FindItemById(wId)
            if not sel.IsChecked():
                self.selectNone()
                self.components.selectNone()
            else:
                self.components.selectComponent(self, self.widgets[`wId`])
                sel.Check(true)
                self.selection = sel
            event.Skip()

    def selectNone(self):
        if self.selection:
            if self.palette.paletteStyle == 'tabs':
                self.selection.SetToggle(false)
                self.selection.Refresh()
                self.selection = None
            elif self.palette.paletteStyle == 'menu':
                self.selection.Check(false)
                self.selection = None


class ZopePalettePage(PalettePage):
    def __init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, components, palette):
        PalettePage.__init__(self, parent, name, bitmapPath, eventOwner, widgets, senders, components, palette)

    def getButtonBmp(self, name, wxClass):
        return IS.load('%s%s.png' %(self.bitmapPath, name))
