#Boa:Dialog:AboutBox

import __version__
__version__ = __version__.ver

from wxPython.wx   import *
from wxPython.html import *
import wxPython.lib.wxpTag
import Preferences

#"#AC76DE"
about_text = '''
<hmtl>
<body bgcolor="#99ccff">
<center>
<table bgcolor="#FFFFFF" width="100%%">
  <tr>
    <td align="center"><h2><br>
    <img src="%s"><br>
    <font color="#006600">Constructor v%s</font></h2></td>
  </tr>
</table>
<p>A RAD GUI building IDE for <b>wxPython</b>
</p>
<p>&copy;2000 <b>Riaan Booysen</b>.<br>
<u>http://boa-constructor.sourceforge.net<br></u>
riaan@e.co.za</p>
<p><font size=-1 color="#000077">wxPlatform: %s %d.%d.%d</font></p>
<hr>
<wxp class="wxButton">
  <param name="label" value="Okay">
  <param name="id"    value="wxID_OK">
</wxp>
</center>
<br><br>
<p>
<p>
<center>
<font size=-1><i>for <font color="#AA0000"><b>Bonnie</b></font></i></font>
</center>
</p>
</body>
</html>
'''

##&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
##&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp
##<wxp class="wxButton">
##  <param name="label" value="News">
##  <param name="id"    value="wxID_YES">
##</wxp>



##<table bgcolor="#99ccff" width="100%%">
##  <tr>
##    <td align="center"><hr></td>
##    <td align="center"><center>
##      <font size=-1><i>for <font color="#AA0000"><b>Bonnie</b></font></i></font>
##    </center></td>
##    <td align="center"><hr></td>
##  </tr>
##</table>
##


def create(parent):
    return wxDialog1(parent)

[wxID_ABOUTBOX] = map(lambda _init_ctrls: wxNewId(), range(1))

class AboutBox(wxDialog):

    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxDialog.__init__(self, size = wxSize(380,525), pos = (-1, -1), id = wxID_ABOUTBOX, title = 'About Boa Constructor', parent = prnt, name = 'AboutBox', style = wxDEFAULT_DIALOG_STYLE)        
        
    def __init__(self, parent): 
        self._init_utils()
        self._init_ctrls(parent)

	self.SetBackgroundColour(wxBLACK)
	self.html = wxHtmlWindow(self, -1 )
	self.html.SetPage(about_text % (Preferences.toPyPath('Images/Shared/Boa.jpg'),
	  __version__, wxPlatform, wxMAJOR_VERSION, wxMINOR_VERSION, wxRELEASE_NUMBER))
	self.SetAutoLayout(true)
	lc = wxLayoutConstraints()
	lc.top.SameAs(self, wxTop, 5)
	lc.left.SameAs(self, wxLeft, 5)
	lc.bottom.SameAs(self, wxBottom, 5)
	lc.right.SameAs(self, wxRight, 5)
	self.html.SetConstraints(lc)
	self.Layout()
	self.Center(wxBOTH)
#        EVT_BUTTON(self, wxID_OK, self.OnOk)
        EVT_BUTTON(self, wxID_YES, self.OnNews)
#	EVT_CLOSE(self, self.OnCloseWindow)
        self.SetAcceleratorTable(wxAcceleratorTable([(0, WXK_ESCAPE, wxID_OK),]))
    
    def OnNews(self, event):
        self.html.LoadPage('http://boa-constructor.sourceforge.net/News.html')

##    def OnCloseWindow(self, event):
##        self.Destroy()
##        event.Skip()












