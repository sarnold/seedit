#!/usr/bin/python -u
#All Rights Reserved (C) 2006, Yuichi Nakmura himainu-ynakam@miomio.jp

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import sys
import gettext
sys.path.insert(0,"/usr/lib")
from  seedit.ui.GUICommon import *
from  seedit.ui.UILogic import *

class tabCommon(gtk.Frame):
	def getTab(self):
		return self

	def __init__(self,name):
		gtk.Frame.__init__(self)
		self.mName = name
		



class fileTab(tabCommon):
	def browseButtonCallBack(self, data=None):
		dialog = fileSelectionDialog()
		r=dialog.run()
		if r ==gtk.RESPONSE_OK:
			selected= dialog.getSelected()
			self.mFileEntry.set_text(selected)
			
	def dirRadioCallBack(self,widget,data=None):
		if widget.get_active() == 1:
			self.mDir=data


	def setPermissionButton(self, permission,value):
		self.mPermission[permission]=value
		self.mPermissionButton[permission].set_active(value)
				 
	def permissionCheckButtonCallBack(self,widget,data):
		if self.mPermission.has_key(data):
			pass
		else:
			print "No key %s" % data
			return

		value = widget.get_active()
		self.mPermission[data]=value

		if data  == 'r':
			self.setPermissionButton('s',value)
		elif data == 'x':
			self.setPermissionButton('r',value)
			self.setPermissionButton('s',value)
		elif data =='w':
			self.setPermissionButton('r',value)
			self.setPermissionButton('s',value)

		elif data in ('a', 'o','c','e', 't'):
			self.setPermissionButton('r',value)
			self.setPermissionButton('s',value)

			

	def addPermissionCheckButton(self, hbox, permission, label):		
		button = gtk.CheckButton(label)
		self.mReadAllLogFlag=False
		button.connect("toggled", self.permissionCheckButtonCallBack, permission)
		hbox.pack_start(button, False)
		self.mPermissionButton[permission]=button
		
	     
	def __init__(self,name):
		tabCommon.__init__(self,name)
		frame = self
		vbox = gtk.VBox()
		frame.add(vbox)
		hbox = gtk.HBox()
		vbox.pack_start(hbox,False)
		label=gtk.Label("File/Dir name:")
		hbox.pack_start(label,False)		
		entry = gtk.Entry()
#		entry.set_max_length(200)
		self.mFileEntry=entry
		hbox.pack_start(entry,False)		
		button = gtk.Button(_("Browse"))
		button.connect("clicked", self.browseButtonCallBack)
		hbox.pack_start(button, False, False, 5)

		#Radios
		self.mDir="itself" 
		hbox=gtk.HBox()
		vbox.pack_start(hbox,False)
		radio = gtk.RadioButton(None, _("Itself"))
		radio.connect("toggled", self.dirRadioCallBack, "itself")
		radio.set_active(True)
		hbox.pack_start(radio, False, False, 5)

		radio = gtk.RadioButton(radio, _("All files in directory"))
		radio.connect("toggled", self.dirRadioCallBack, "direct")
		hbox.pack_start(radio, False, False, 5)

		radio = gtk.RadioButton(radio, _("All files in directory,subdirectories"))
		radio.connect("toggled", self.dirRadioCallBack, "all")
		hbox.pack_start(radio, False, False, 5)
		
		#Permissions
		self.mPermission = {'s':False, 'r':False, 'x':False, 'w':False, 'a':False, 'o':False, 'c':False, 'e':False, 't':False}
		self.mPermissionButton =dict()
		pFrame=gtk.Frame(_("Permissoins"))
		vbox.pack_start(pFrame,False)
		pVbox=gtk.VBox()
		pFrame.add(pVbox)
		hbox = gtk.HBox()
		pVbox.pack_start(hbox, False)

		self.addPermissionCheckButton(hbox,"s",_("s(Search)"))
		self.addPermissionCheckButton(hbox,"r",_("r(Read)"))
		self.addPermissionCheckButton(hbox,"x",_("x(eXecute)"))
		
		hbox = gtk.HBox()
		pVbox.pack_start(hbox, False)
		self.addPermissionCheckButton(hbox,"w",_("w(Write)"))

		expander = gtk.Expander(_("Detailed write Permission"))
		hbox.pack_start(expander, False)
		pVbox=gtk.VBox()
		expander.add(pVbox)
		hbox = gtk.HBox()
		pVbox.pack_start(hbox, False)
		self.addPermissionCheckButton(hbox,"a",_("a(Append)"))
		self.addPermissionCheckButton(hbox,"o",_("o(Overwrite)"))
		self.addPermissionCheckButton(hbox,"c",_("c(Create)"))
		self.addPermissionCheckButton(hbox,"e",_("e(Erase)"))
		self.addPermissionCheckButton(hbox,"t",_("t(seTattr)"))

class networkTab(tabCommon):
	def behaviorCheckButtonCallBack(self,widget,data):
		value = widget.get_active()

		if data=="server":
			self.mServerFlag=value
		elif data=="client":
			self.mClientFlag=value
		
		
	def protocolRadioCallBack(self,widget,data=None):
		if widget.get_active() == 1:
			self.mProtocol=data
	def portRadioCallBack(self,widget,data=None):
		if widget.get_active() == 1:
			self.mPortType=data
			
	def __init__(self,name):
		tabCommon.__init__(self,name)
		frame = self
		frameVbox = gtk.VBox()
		frame.add(frameVbox)

		#protocol
		self.mProtocol="tcp"
		frame = gtk.Frame(_("Protocol"))
		frameVbox.pack_start(frame,False)
		hbox=gtk.HBox()
		frame.add(hbox)
		radio = gtk.RadioButton(None, "tcp")
		radio.connect("toggled", self.protocolRadioCallBack, "tcp")
		radio.set_active(True)
		hbox.pack_start(radio,False)
		radio = gtk.RadioButton(radio, "udp")
		radio.connect("toggled", self.protocolRadioCallBack, "udp")
		hbox.pack_start(radio,False)
		radio = gtk.RadioButton(radio, "raw")
		radio.connect("toggled", self.protocolRadioCallBack, "raw")
		hbox.pack_start(radio,False)
		
		#Port
		self.mPort=""
		self.mPortType="specific" #specific is specific number, all is *, wellknown is -1023, unpriv is 1024-
		frame = gtk.Frame(_("Port"))
		frameVbox.pack_start(frame,False)
		vbox=gtk.VBox()
		frame.add(vbox)
		
		hbox=gtk.HBox()
		vbox.pack_start(hbox,False)
		radio = gtk.RadioButton(None, _("Specific Number:"))
		radio.connect("toggled", self.portRadioCallBack, "specific")
		hbox.pack_start(radio,False)
		entry = gtk.Entry()
		entry.set_max_length(40)
		self.mPortEntry = entry
		hbox.pack_start(entry,False)
		
		hbox=gtk.HBox()
		vbox.pack_start(hbox,False)
		radio = gtk.RadioButton(radio, _("All unreserved wellknown ports"))
		radio.connect("toggled", self.portRadioCallBack, "wellknown")
		hbox.pack_start(radio,False)
		
		radio = gtk.RadioButton(radio, _("All ports over 1024"))
		radio.connect("toggled", self.portRadioCallBack, "unpriv")
		hbox.pack_start(radio,False)
		radio = gtk.RadioButton(radio, _("All ports"))
		radio.connect("toggled", self.portRadioCallBack, "all")
		hbox.pack_start(radio,False)
		
         	#Behavior
		self.mServerFlag=False
		self.mClientFlag=False
		frame = gtk.Frame(_("Behavior"))
		frameVbox.pack_start(frame,False)
		hbox=gtk.HBox()
		frame.add(hbox)
		button = gtk.CheckButton(_("Server"))
		button.connect("toggled", self.behaviorCheckButtonCallBack, "server")
		hbox.pack_start(button, False)

		button = gtk.CheckButton(_("Client"))
		button.connect("toggled", self.behaviorCheckButtonCallBack, "client")
		hbox.pack_start(button, False)
		

class insertPolicyWindow(seeditCommon):
	def allowFile(self):
		tab = self.mFileTab.getTab()
		file = tab.mFileEntry.get_text()
		dirType =  tab.mDir
		permission = tab.mPermission


		str = allowFileStr(file,dirType,permission)
		return str

	def allowNetwork(self):
		tab = self.mNetworkTab.getTab()
		protocol = tab.mProtocol
		portType= tab.mPortType
		portText = tab.mPortEntry.get_text()

		serverFlag =tab.mServerFlag
		clientFlag =tab.mClientFlag
			
		str = allowNetStr(protocol, portType, portText, serverFlag, clientFlag)

		return str

	def closeCallBack(self,data=None):
		self.mWindow.destroy()

	def addCallBack(self,widget,data):
		notebook=data
		page=notebook.get_current_page()
		tab = notebook.get_nth_page(page)
		name = tab.mName
		if name=="file":
			str = self.allowFile()
		elif name=="network":
			str = self.allowNetwork()
		else:
			str=""

		if str=="":
			return
		else:
			buf = self.mParent.mTextBuffer
			buf.insert_at_cursor(str)
			self.mWindow.destroy()
	
	def __init__(self,parent):
		self.mParent = parent
		window = gtk.Window()
		self.mWindow = window
		window.set_title(_("Insert Policy"))
		vbox =gtk.VBox()
		window.add(vbox)


		notebook = gtk.Notebook()
		notebook.set_tab_pos(gtk.POS_TOP)
		vbox.pack_start(notebook)
		tab1 = fileTab("file")
		self.mFileTab=tab1
		label = gtk.Label(_("File"))
		notebook.append_page(tab1.getTab(), label)

		tab2 = networkTab("network")
		self.mNetworkTab=tab2
		 
		label = gtk.Label(_("Network"))
		notebook.append_page(tab2.getTab(), label)
		hbox =gtk.HButtonBox()
		button = gtk.Button(_("Add"),gtk.STOCK_ADD)
		button.connect("clicked", self.addCallBack,notebook)			       

		hbox.pack_start(button,False)
		button = gtk.Button(_("Close"),gtk.STOCK_CLOSE)
		button.connect("clicked", self.closeCallBack)			       
		hbox.pack_start(button,False)

		vbox.pack_start(hbox,False)
		window.show_all()

class openDomainDialog(gtk.Dialog):

	def getOpenDomain(self):
		return self.mDomain
	
	
	def domainListComboCallBack(self,widget,data=None):
		self.mDomain= widget.get_active_text()

	def openFile(self):
		domain = self.mDomain
		if re.search("\.sp$",domain):
			filename = gSPPath +"/"+domain
		else:
			filename = gSPPath +"/"+domain+".sp"
		try:
			input = open(filename,'r')
		except:
			return None
		return input
			

	def show(self):
		r = self.run()
		self.destroy()
		return r
	def __init__(self,parent):
		self.mParentWindow = parent
		gtk.Dialog.__init__(self,_("Open domain"),parent.mWindow, gtk.DIALOG_MODAL,(gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
		hbox = gtk.HBox()
		label = gtk.Label(_("Select domain:"))
		hbox.pack_start(label, False, False,5)
		combo = gtk.combo_box_entry_new_text()
		self.mDomainListComboBox = combo
		self.mDomain=""
		domainList = getEditableDomainList()
		for domain in domainList:
			combo.append_text(domain)
		combo.connect('changed', self.domainListComboCallBack)
		self.vbox.pack_start(combo,False)

		self.show_all()
	


class seeditEditWindow(seeditCommon):
    ui = '''<ui>
    <menubar name="MenuBar">
      <menu action="Help">
        <menuitem action="About"/>
      </menu>
     </menubar>
      <toolbar name="ToolBar">
      <toolitem action="Open"/>
      <separator/>
      <toolitem action="Save"/>
      <separator/>
      <toolitem action="Add"/>
    </toolbar>
    </ui>'''

    def SaveCallBack(self,data=None):
	    if self.mDomain == "":
		    return
	    buf = self.mTextBuffer
	    start = buf.get_start_iter()
	    end = buf.get_end_iter()
	    str = buf.get_text(start, end)

	    filename = getDomainFileName(self.mDomain)
	    r = saveStringToFile(str,filename)
	    if r != SEEDIT_SUCCESS:
		    self.showMessageDialog(gtk.MESSAGE_ERROR, _("File open Error:%s. \n")%(filename))
		    return
	    
	    ld=loadPolicyDialog(self)
	    (s, data) = ld.do()
	    if s<0:
		    msg = _("%s:Syntax error in line %s") % (self.mDomain,data)
		    lineno=int(data) -1
		    start =  buf.get_start_iter()
		    start.set_line(lineno)
		    end = buf.get_start_iter()
		    end.set_line(lineno+1)
		    tag = buf.get_tag_table()
		    tag = buf.create_tag(background="red")
		    buf.apply_tag(tag,start,end)
		    r = saveStringToFile(self.mBackupLines, filename)
		    if r != SEEDIT_SUCCESS:
			    self.showMessageDialog(gtk.MESSAGE_ERROR, _("File open Error:%s. \n")%(filename))
			    return
	    else:
		    msg = _("%s:load success") % (self.mDomain)
		    self.mBackupLines = str
		    
	    self.mStatusLabel.set_text(msg)

	  

    def OpenCallBack(self,data=None):
	    dialog = openDomainDialog(self)
	    r = dialog.show()
	    if r==gtk.RESPONSE_CANCEL:
		    return
	    input = dialog.openFile()
	    if input ==None:
		    self.showMessageDialog(gtk.MESSAGE_ERROR, _("File open Error.\n"))
		    return

	    lines = input.readlines()
	    self.mBackupLines=""
	    for l in lines:
		    self.mBackupLines = self.mBackupLines + l
	    
	    self.mTextBuffer.delete(self.mTextBuffer.get_start_iter(),self.mTextBuffer.get_end_iter())
	    
	    for line in lines:
		    self.mTextBuffer.insert(self.mTextBuffer.get_end_iter(),line)
	    self.mDomain = dialog.getOpenDomain()
	    self.mStatusLabel.set_text(_("Editing %s") % (self.mDomain))
	    print "Open"
	    pass
    def AddCallBack(self,data=None):
	    window = insertPolicyWindow(self)

    def initMenu(self,window):
        uimanager = gtk.UIManager()
	accelgroup = uimanager.get_accel_group()
        window.add_accel_group(accelgroup)
	actiongroup = gtk.ActionGroup('seeditUIManager')
        self.actiongroup = actiongroup
	actiongroup.add_actions([ ('About', gtk.STOCK_ABOUT,_("_About"), None,
                                  _('About'), self.showAbout),
                                 ('Help', None, _('_Help')),



				  ('Save', gtk.STOCK_SAVE, "_Save", None,_("Save and apply"), self.SaveCallBack),
				  ('Open', gtk.STOCK_OPEN, "_Open", None,_("Open domain"), self.OpenCallBack),
				  ('Add', gtk.STOCK_ADD, "_Add", None,_("Add policy"), self.AddCallBack),
				  
				  ])
        uimanager.insert_action_group(actiongroup, 0)
        uimanager.add_ui_from_string(self.ui)
	menubar = uimanager.get_widget('/MenuBar')
	toolbar = uimanager.get_widget('/ToolBar')
        return (menubar,toolbar)


    def __init__(self):
        window = gtk.Window()
        self.mWindow = window
	self.mDomain =""
	self.mBackupLines="" # Contents of file before save
        window.set_title(_("seedit policy editor"))
        window.connect('destroy', lambda w: gtk.main_quit())

        vbox = gtk.VBox()
        window.add(vbox)

	(menubar, toolbar)=self.initMenu(self.mWindow)
	vbox.pack_start(menubar,False)
	vbox.pack_start(toolbar,False)

	sw = gtk.ScrolledWindow()
        sw.set_size_request(300,200)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        textbuffer = textview.get_buffer()
        self.mTextBuffer= textbuffer
        sw.add(textview)
	vbox.pack_start(sw,True)

	label=gtk.Label(_(""))
	self.mStatusLabel = label
	vbox.pack_start(label,False)
	window.show_all()
	
            
if __name__ == '__main__':
    gettext.install("seedit-gui","/usr/share/locale")
    seeditEditWindow()
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
