#-----------------------------------------------------------------------------
# Name:        sourceconst.py
# Purpose:     Central place for constants, templates and snippets used by the
#              code generation process
#
# Author:      Riaan Booysen
#
# Created:     2001/19/02
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2003 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------

import os

import Preferences, Utils

idnt = Utils.getIndentBlock()

methodIndent = idnt
bodyIndent = idnt*2

def wsfix(s):
    return s.replace('\t', idnt).replace('\n', os.linesep)


boaIdent = '#Boa'
boaClass = 'BoaApp'

init_ctrls = '_init_ctrls'
init_coll = '_init_coll_'
init_utils = '_init_utils'
init_props = '_init_props'
init_events = '_init_events'
init_sizers = '_init_sizers'
code_gen_warning = "generated method, don't edit"

defEnvPython = wsfix('#!/usr/bin/env python\n')
defImport = wsfix('from wxPython.wx import *\n\n')
defSig = boaIdent+wsfix(':%(modelIdent)s:%(main)s\n\n')

defCreateClass = wsfix('''def create(parent):
\treturn %(main)s(parent)

''')

srchWindowIds = '\[(?P<winids>[A-Za-z0-9_, ]*)\] = '+\
'map\(lambda %s: (wx)*NewId\(\), range\((?P<count>\d+)\)\)'
srchWindowIdsCont = '(?P<any>.*)\] = map\(lambda %s: (wx)*NewId\(\), range\((?P<count>\d+)\)\)'
defWindowIds = wsfix('''[%(idNames)s] = map(lambda %(idIdent)s: wxNewId(), range(%(idCount)d))\n''')
defWindowIdsCont = wsfix('''] = map(lambda %(idIdent)s: wxNewId(), range(%(idCount)d))\n''')

defClass = wsfix('''
class %(main)s(%(defaultName)s):
\tdef '''+init_utils+'''(self):
\t\tpass

\tdef '''+init_ctrls+'''(self, prnt):
\t\t%(defaultName)s.__init__(%(params)s)
\t\tself.'''+init_utils+'''()

\tdef __init__(self, parent):
\t\tself.'''+init_ctrls+'''(parent)
''')

defApp = wsfix('''import %(mainModule)s

modules = {'%(mainModule)s' : [1, 'Main frame of Application', '%(mainModule)s.py']}

class BoaApp(wxApp):
\tdef OnInit(self):
\t\twxInitAllImageHandlers()
\t\tself.main = %(mainModule)s.create(None)
\t\t# needed when running from Boa under Windows 9X
\t\tself.SetTopWindow(self.main)
\t\tself.main.Show();self.main.Hide();self.main.Show()
\t\treturn True

def main():
\tapplication = BoaApp(0)
\tapplication.MainLoop()

if __name__ == '__main__':
\tmain()
''')

defInfoBlock = wsfix('''#-----------------------------------------------------------------------------
# Name:        %(Name)s
# Purpose:     %(Purpose)s
#
# Author:      %(Author)s
#
# Created:     %(Created)s
# RCS-ID:      %(RCS-ID)s
# Copyright:   %(Copyright)s
# Licence:     %(Licence)s
#-----------------------------------------------------------------------------
''')

defSetup_py = wsfix('''
from distutils.core import setup

setup(name = '%(name)s',
      version = '%(version)s',
      scripts = [%(scripts)s],
)
''')

defPackageSrc = wsfix('''# Package initialisation
''')

defPyApp = wsfix('''modules = {}

def main():
\tpass

if __name__ == '__main__':
\tmain()
''')

simpleModuleRunSrc = wsfix('''

if __name__ == '__main__':
\tpass # add a call to run your script here
''')

simpleAppFrameRunSrc = wsfix('''

if __name__ == '__main__':
\tapp = wxPySimpleApp()
\twxInitAllImageHandlers()
\tframe = create(None)
\t# needed when running from Boa under Windows 9X
\tframe.Show();frame.Hide();frame.Show()

\tapp.MainLoop()
''')

simpleAppDialogRunSrc = wsfix('''

if __name__ == '__main__':
\tapp = wxPySimpleApp()
\twxInitAllImageHandlers()
\tdlg = create(None)
\ttry:
\t\tdlg.ShowModal()
\tfinally:
\t\tdlg.Destroy()
\tapp.MainLoop()
''')

simpleAppPopupRunSrc = wsfix('''

if __name__ == '__main__':
\tapp = wxPySimpleApp()
\twxInitAllImageHandlers()
\tframe = wxFrame(None, -1, 'Parent')
\tframe.SetAutoLayout(True)
\tframe.Show()
\tpopup = create(frame)
\tpopup.Show(True)
\tapp.MainLoop()
''')
