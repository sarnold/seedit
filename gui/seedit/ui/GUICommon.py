#!/usr/bin/python -u

#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura
#! Copyright (c) 2006 SELinux Policy Editor Team
#! This program is free software; you can redistribute it and/or modify
#! it under the terms of the GNU General Public License as published by
#! the Free Software Foundation; either version 2 of the License, or
#! (at your option) any later version.
#! 
#! This program is distributed in the hope that it will be useful,
#! but WITHOUT ANY WARRANTY; without even the implied warranty of
#! MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#! GNU General Public License for more details.
#! 
#! You should have received a copy of the GNU General Public License
#! along with this program; if not, write to the Free Software
#! Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import pygtk
pygtk.require('2.0')
import gtk
import os
import sys
import gettext
import gobject
import locale
import threading
import pwd
sys.path.insert(0,"/usr/lib")
from UILogic import *


class seeditCommon:
    """
    This class is base class for all seedit GUI Window
    """
    ui = '''<ui>
    <menubar name="MenuBar">
      <menu action="Help">
        <menuitem action="Manual"/>
        <menuitem action="About"/>
      </menu>
      
    </menubar>
    </ui>'''

    mVersion = "2.1.0"
    
    #Returns menubar
    def initMenu(self,window):
        # Create a UIManager instance
        uimanager = gtk.UIManager()

        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        window.add_accel_group(accelgroup)

        # Create an ActionGroup
        actiongroup = gtk.ActionGroup('seeditUIManager')
        self.actiongroup = actiongroup

        # Create actions
        actiongroup.add_actions([
                                 ('About', gtk.STOCK_DIALOG_INFO,_("_About"), None,
                                  _('About'), self.showAbout),
                                  ('Manual', gtk.STOCK_HELP,_("_Help"), None,
                                  _('Manual'), self.showManual),
                                 ('Help', None, _('_Help')),
                                 ])

        # Add the actiongroup to the uimanager
        uimanager.insert_action_group(actiongroup, 0)
        # Add a UI description
        uimanager.add_ui_from_string(self.ui)

        # Create a MenuBar
        menubar = uimanager.get_widget('/MenuBar')
        return menubar
    
    def showNotImplementedDialog(self):
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                   _("This feature has not yet been implemented"))
        dialog.run()
        dialog.destroy()

    def showYesNoDialog(self,message):
        dialogType = gtk.MESSAGE_INFO
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   dialogType, gtk.BUTTONS_YES_NO,
                                   message)
        response = dialog.run()
        dialog.destroy()
        return response

    def showMessageDialog(self, type, message):
        
        #if type==SEEDIT_ERROR:
        #    dialogType=gtk.MESSAGE_ERROR
        #elif type==SEEDIT_SUCCESS:
        #    dialogType=gtk.MESSAGE_INFO
        #elif type==SEEDIT_INFO :
        #    dialogType=gtk.MESSAGE_INFO

        dialogType = type
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   dialogType, gtk.BUTTONS_OK,
                                   message)
        dialog.run()
        dialog.destroy()
    
    def notImplementedCallBack(self,w,data=None):
        self.showNotImplementedDialog()

    def showManual(self,data=None):
        argv=[]
        argv.append("/usr/bin/firefox")
        
        uri = "http://seedit.sourceforge.net/"
                
        argv.append(uri)
        
        prevusername=  os.environ["USER"]
        prevlogname= os.environ["LOGNAME"]
   
        if os.environ.has_key("USERHELPER_UID"):
            uidstr = os.environ["USERHELPER_UID"]
            prevuid= os.getuid()
            uid = int(uidstr)
            username = pwd.getpwuid(uid)[0]
            os.environ["USER"]=username
            os.environ["LOGNAME"]= username
        try:
            gobject.spawn_async(argv)
        except:
            message =_("There was a problem launching the web browser")
            self.showMessageDialog(gtk.MESSAGE_ERROR,message)
        os.environ["USER"]=prevusername
        os.environ["LOGNAME"]= prevlogname
            
    def showAbout(self,data=None):
        message = _("SELinux Policy Editor GUI\nVersion %s\n") % (self.mVersion) 
        message += _("All rights reserved (c) 2006 SELinux Policy Editor Team\n")
        message += _("This software is distributed under the GNU GPL.\n")
        message += _("For more information, visit http://seedit.sourceforge.net/\n")
        self.showMessageDialog(gtk.MESSAGE_INFO,message)

    def checkOverWrite(self, filename):

        if os.path.exists(filename):
            response = self.showYesNoDialog(_("The file %s already exists. \n Overwrite this file?")% (filename))
            if response == gtk.RESPONSE_YES:
                return True
            elif response == gtk.RESPONSE_NO:
                return False
        return True

    def yesNoSelection(self, message, default, callback):
        hbox = gtk.HBox()
        label = gtk.Label(message)
        hbox.pack_start(label, False, False,5)
        radio = gtk.RadioButton(None, _("Yes"))
        self.mDaemonFlag = True
        radio.connect("toggled", callback, True)
        if default == True:
            radio.set_active(True)

        hbox.pack_start(radio, False, False,5)
        radio = gtk.RadioButton(radio, _("No"))
        if default == False:
            radio.set_active(True)
        radio.connect("toggled", callback, False)
        
        
        hbox.pack_start(radio, False, False,5)

        return hbox
   
    #In Cent OS4, get_active_text is not supported
    def get_active_text(self,widget):
        index = widget.get_active()
        if index <0:
            return ""
        model = widget.get_model()
        text = model[index][0]
        return text

    def getInsertPointOfTextBuf(self,textBuffer):
        buf = textBuffer
        iter = buf.get_start_iter()
        
        while not iter.is_end():
            iter.forward_char()
            char = iter.get_char()
            if char == '}':
                return iter
        return None

    def insertStrAtTextBuf(self,textBuffer,str):
        buf = self.mTextBuffer
        iter = self.getInsertPointOfTextBuf(buf)
        if iter:
            buf.insert(iter,str)
        else:
            buf.insert_at_cursor(str)


class loadPolicyThread(threading.Thread):

    def updateTextBuffer(self, line):
        self.mDialog.mTextBuffer.insert(self.mDialog.mTextBuffer.get_end_iter(),line)

    
    def __init__(self,dialog,command, closeFlag=False):
        if command == None:
            command = gSeeditLoad +" -v"

        self.mCommand = command
        self.mErrorLine=""
        self.mCloseFlag=closeFlag
        threading.Thread.__init__(self)
        self.mDialog = dialog

    def run(self):

        command = self.mCommand
        input=os.popen(command, "r")

        line = input.readline()
        while line:
            gobject.idle_add(self.updateTextBuffer,line)
            if re.search("seedit-converter:Error:",line):
                self.mErrorLine=line

            line = input.readline()
            sys.stdout.write(line)
                        
        
        if input.close():
            self.mDialog.set_response_sensitive(gtk.RESPONSE_CANCEL,True)
            gobject.idle_add(self.mDialog.mLabel.set_text, _("There is a Syntax Error"))

            return SEEDIT_ERROR_SEEDIT_LOAD

        gobject.idle_add(self.mDialog.mLabel.set_text, _("Completed"))

        if self.mCloseFlag:
            self.mDialog.response(gtk.RESPONSE_OK)
            self.mDialog.destroy()
        else:
            self.mDialog.set_response_sensitive(gtk.RESPONSE_CANCEL,True)
            self.mDialog.response(gtk.RESPONSE_OK)
            self.mDialog.destroy()
        return gtk.RESPONSE_OK




'''
Dialog that shows progress of seedit-load
'''
class loadPolicyDialog(gtk.Dialog):
    def dummyCallback(self,data =None):
        pass
    def showCallback(self, data=None):
        thread = loadPolicyThread(self,self.mCommand,self.mCloseFlag)
        self.mThread = thread
        thread.start()

    '''
    returns error code and data(such as error description)
    '''
    def do(self):
        r = self.run()
        self.destroy()
        if r==gtk.RESPONSE_OK:
            return (SEEDIT_SUCCESS,None)
        else:
            lineno=""
            errLine = self.mThread.mErrorLine
            m = re.search("line[\s\t]+\d+",errLine)
            if m:
                l=m.group().split()
                lineno =l[1]
                    
            return (SEEDIT_ERROR_SEEDIT_LOAD,lineno)

    def __init__(self,parent,closeFlag=True,title=None, message=None,command=None):
        if title == None:
            title=_("Load policy")

        if message==None:
            message=_("Loading Policy. This make take a while. Please do not close the window.")

        self.mCloseFlag=closeFlag # if False, dialog will not close even if success
        self.mParentWindow=parent
        gtk.Dialog.__init__(self,title,parent.mWindow, gtk.DIALOG_MODAL,(gtk.STOCK_OK, gtk.RESPONSE_CANCEL))
        if command ==None:
            self.mCommand = gSeedit_load+" -v"
        else:
            self.mCommand = command
        
        self.set_response_sensitive(gtk.RESPONSE_CANCEL,False)
        
        self.set_decorated(False)
        
        label= gtk.Label(message)
        self.mLabel = label
        self.vbox.pack_start(label, False, False,0)

        expander = gtk.Expander(_("Details"))
        self.vbox.pack_start(expander,False,False,0)
        sw = gtk.ScrolledWindow()
        sw.set_size_request(300,200)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        textbuffer = textview.get_buffer()
        self.mTextBuffer= textbuffer
        sw.add(textview)
        expander.add(sw)
        self.connect("show", self.showCallback)
        self.show_all()
   
        
     
class fileSelectionDialog(gtk.FileSelection):
	def getSelected(self):
		return self.mFileName
	def okCallBack(self, w):
		self.mFileName= self.get_filename()
		self.response(gtk.RESPONSE_OK)
		self.destroy()
	def cancelCallBack(self, w):
		self.response(gtk.RESPONSE_CANCEL)
		self.destroy()
	
	def  __init__(self,title=None):
		self.mFileName=""
		gtk.FileSelection.__init__(self,title)
		self.ok_button.connect("clicked", self.okCallBack)
		
		self.cancel_button.connect("clicked",self.cancelCallBack)
		self.show()


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
		label=gtk.Label(_("File/Dir name:"))
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
		hbox=gtk.VBox()
		vbox.pack_start(hbox,False)
		radio = gtk.RadioButton(None, _("Itself"))
		radio.connect("toggled", self.dirRadioCallBack, "itself")
		radio.set_active(True)
		hbox.pack_start(radio, False, False)

		radio = gtk.RadioButton(radio, _("All files in directory"))
		radio.connect("toggled", self.dirRadioCallBack, "direct")
		hbox.pack_start(radio, False, False)

		radio = gtk.RadioButton(radio, _("All files in directory, subdirectories"))
		radio.connect("toggled", self.dirRadioCallBack, "all")
		hbox.pack_start(radio, False, False)
		
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

		expander = gtk.Expander(_("Detailed write permission"))
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
		
		hbox=gtk.VBox()
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


        def getInsertPoint(self,textBuffer):
            buf = textBuffer
            iter = buf.get_start_iter()
            
            while not iter.is_end():
                iter.forward_char()
                char = iter.get_char()
                if char == '}':
                    return iter
            return None
                
                           
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
			buf = self.mTextBuffer
                        iter = self.getInsertPoint(buf)
                        if iter:
                            buf.insert(iter,str)
                        else:
                            buf.insert_at_cursor(str)
			self.mWindow.destroy()
	
	def __init__(self,parent,textBuffer):
		self.mParent = parent
                self.mTextBuffer = textBuffer
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


class editTemplateFrame(seeditCommon):  
    def saveButtonCallBack(self, data=None):
        filename = self.mToBeSavedFile
        start = self.mTextBuffer.get_start_iter()
        end = self.mTextBuffer.get_end_iter()
        data = self.mTextBuffer.get_text(start,end)
                
        if not self.checkOverWrite(filename):
            self.showMessageDialog(gtk.MESSAGE_INFO, _("Save cancelled.\n"))
            return

        r = saveStringToFile(data,filename)
        if r<0:
            self.showMessageDialog(gtk.MESSAGE_INFO, _("File write error. Save cancelled.\n"))
            return

        ld=loadPolicyDialog(self.mParentWindow)
        (s, data) = ld.do()

        if s<0:
            os.unlink(filename)
            self.showMessageDialog(gtk.MESSAGE_INFO, _("Syntax error was found.\n"))


            return
        else:

            self.showMessageDialog(gtk.MESSAGE_INFO, _("Domain created successfully.\n"))
               
        return

    def addButtonCallBack(self,data=None):
        window = insertPolicyWindow(self,self.mTextBuffer)

    #Guess policy by rpm -ql command
    def generateButtonCallBack(self,data=None):
        if self.mPath:
            addString = guessRelatedFileAllow(self.mPath)
            if addString != "":
                self.insertStrAtTextBuf(self.mTextBuffer,addString)
        
    def __init__(self,parentWindow,frameTitle,textBufferTitle):
        self.mParentWindow = parentWindow
        frame = gtk.Frame(frameTitle)
        self.mFrame = frame
        vbox = gtk.VBox()
        frame.add(vbox)
        hbox = gtk.HBox()
        label = gtk.Label(textBufferTitle)
        hbox.pack_start(label,False,False,5)
        label = gtk.Label("")
        self.mToBeSavedFileLabel= label
        self.mToBeSavedFile=None
        self.mPath = None
        
        hbox.pack_start(label,False,False,5)
        vbox.pack_start(hbox,False,False,0)
        
        sw = gtk.ScrolledWindow()
        sw.set_size_request(300,200)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        textbuffer = textview.get_buffer()
        self.mTextBuffer= textbuffer
        sw.add(textview)
        vbox.pack_start(sw, True, True, 5)
        
        hbox = gtk.HBox()
        button = gtk.Button(_("Add policy"))
        hbox.pack_start(button, False, False, 5)
        button.connect("clicked", self.addButtonCallBack)
        
        button = gtk.Button(_("Generate more policy"))
        hbox.pack_start(button, False, False, 5)
        button.connect("clicked", self.generateButtonCallBack)
        
        button = gtk.Button(_("Save and Apply"))
        hbox.pack_start(button, False, False, 5)
        button.connect("clicked", self.saveButtonCallBack)
        vbox.pack_start(hbox, False, False, 5)
        
