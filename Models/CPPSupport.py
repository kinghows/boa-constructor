#-----------------------------------------------------------------------------
# Name:        CPPSupport.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2004
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.CPPSupport'

import os

from wxPython import wx

import Preferences, Utils

true=1;false=0

import EditorHelper
EditorHelper.imgCPPModel = EditorHelper.imgIdxRange()

from Models.EditorModels import SourceModel
class CPPModel(SourceModel):
    modelIdentifier = 'CPP'
    defaultName = 'cpp'
    bitmap = 'Cpp_s.png'
    imgIdx = EditorHelper.imgCPPModel
    ext = '.cxx'

    def __init__(self, data, name, editor, saved):
        SourceModel.__init__(self, data, name, editor, saved)
        self.loadHeader()
        if data: self.update()

    def loadHeader(self):
        header = os.path.splitext(self.filename)[0]+'.h'
        if os.path.exists(header):
            # This should open a BasicFileModel instead of a file directly
            self.headerData = open(header).read()
        else:
            self.headerData = ''

    def load(self, notify=true):
        SourceModel.load(self, false)
        self.loadHeader()
        self.update()
        if notify: self.notify()

EditorHelper.modelReg[CPPModel.modelIdentifier] = CPPModel
from EditorHelper import extMap
extMap['.cpp'] = extMap['.c'] = extMap['.h'] = CPPModel

from Views.StyledTextCtrls import LanguageSTCMix, FoldingStyledTextCtrlMix, stcConfigPath
class CPPStyledTextCtrlMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId,
              (0, Preferences.STCLineNumMarginWidth), 'cpp', stcConfigPath)
        self.setStyles()

wxID_CPPSOURCEVIEW = wx.wxNewId()
symbolFolding = 1
from Views.SourceViews import EditorStyledTextCtrl
class CPPSourceView(EditorStyledTextCtrl, CPPStyledTextCtrlMix, FoldingStyledTextCtrlMix):
    viewName = 'Source'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_CPPSOURCEVIEW,
          model, (), -1)
        CPPStyledTextCtrlMix.__init__(self, wxID_CPPSOURCEVIEW)
        FoldingStyledTextCtrlMix.__init__(self, wxID_CPPSOURCEVIEW, symbolFolding)
        self.active = true

    def OnMarginClick(self, event):
        FoldingStyledTextCtrlMix.OnMarginClick(self, event)

class HPPSourceView(CPPSourceView):
    viewName = 'Header'
    def __init__(self, parent, model):
        CPPSourceView.__init__(self, parent, model)

    def refreshCtrl(self):
        self.pos = self.GetCurrentPos()
        prevVsblLn = self.GetFirstVisibleLine()

        self.SetText(self.model.headerData)
        self.EmptyUndoBuffer()
        self.GotoPos(self.pos)
        curVsblLn = self.GetFirstVisibleLine()
        self.LineScroll(0, prevVsblLn - curVsblLn)

        self.nonUserModification = false
        self.updatePageName()

from Explorers import ExplorerNodes
ExplorerNodes.langStyleInfoReg.append( ('CPP', 'cpp', CPPStyledTextCtrlMix,
      'stc-styles.rc.cfg') )

import Controllers
class CPPController(Controllers.SourceController):
    Model           = CPPModel
    DefaultViews    = [CPPSourceView, HPPSourceView]

Controllers.modelControllerReg[CPPModel] = CPPController

import PaletteStore
PaletteStore.newControllers['Cpp'] = CPPController
PaletteStore.paletteLists['New'].append('Cpp')
