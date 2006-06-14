#!/usr/bin/python -u

import pygtk
pygtk.require('2.0')
import gtk
import os
import sys
import gettext
import gobject
import threading
sys.path.insert(0,"/usr/lib")
from UILogic import *


class seeditCommon:
    """
    This class is base class for all seedit GUI Window
    """
    ui = '''<ui>
    <menubar name="MenuBar">
      <menu action="Help">
        <menuitem action="About"/>
      </menu>
      
    </menubar>
    </ui>'''

    mVersion = "2.0.0"
    
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
                                 ('About', gtk.STOCK_ABOUT,_("_About"), None,
                                  _('About'), self.showAbout),
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
                                   _("Sorry! This is not implemented yet"))
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
        
    def showAbout(self,data=None):
        message = _("SELinux Policy Editor GUI\nVersion %s\n") % (self.mVersion) 
        message += _("All rights reserved (c) 2006 Yuichi Nakamura\n")
        message += _("This software is distributed under GPL.\n")
        message += _("For more information, visit http://seedit.sourceforge.net/\n")
        self.showMessageDialog(gtk.MESSAGE_INFO,message)

    def checkOverWrite(self, filename):

        if os.path.exists(filename):
            response = self.showYesNoDialog(_("File %s already exists. \n Overwrite?")%(filename))
            if response == gtk.RESPONSE_YES:
                return True
            elif response == gtk.RESPONSE_NO:
                return False
        return True

  

class loadPolicyThread(threading.Thread):

    def updateTextBuffer(self, line):
        self.mDialog.mTextBuffer.insert(self.mDialog.mTextBuffer.get_end_iter(),line)

    
    def __init__(self,dialog):
        self.mErrorLine=""
        threading.Thread.__init__(self)
        self.mDialog = dialog

    def run(self):
        command = gSeedit_load+" -v"

        input=os.popen(command, "r")

        line = input.readline()
        while line:
            gobject.idle_add(self.updateTextBuffer,line)
            if re.search("seedit-converter:Error:",line):
                self.mErrorLine=line
#            self.mDialog.mTextBuffer.insert(self.mDialog.mTextBuffer.get_end_iter(),line)
            line = input.readline()
            sys.stdout.write(line)
        
        if input.close():
            self.mDialog.set_response_sensitive(gtk.RESPONSE_CANCEL,True)
            gobject.idle_add(self.mDialog.mLabel.set_text, _("Error:Syntax Error"))
            #          self.mDialog.mLabel.set_text(_("Error:Syntax Error"))
#            self.mDialog.response(gtk.RESPONSE_CANCEL)
            return SEEDIT_ERROR_SEEDIT_LOAD

        gobject.idle_add(self.mDialog.mLabel.set_text, _("Success!"))
#        self.mDialog.mLabel.set_text(_("Success!!"))

        
        self.mDialog.response(gtk.RESPONSE_OK)
        self.mDialog.destroy()

        return SEEDIT_SUCCESS
            
'''
Dialog that shows progress of seedit-load
'''
class loadPolicyDialog(gtk.Dialog):
    def dummyCallback(self,data =None):
        pass
    def showCallback(self, data=None):
        thread = loadPolicyThread(self)
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

    def __init__(self,parent):
        self.mParentWindow=parent
        gtk.Dialog.__init__(self,_("load policy"),parent.mWindow, gtk.DIALOG_MODAL,(gtk.STOCK_OK, gtk.RESPONSE_CANCEL))
        self.set_response_sensitive(gtk.RESPONSE_CANCEL,False)
        
        self.set_decorated(False)
        
        label= gtk.Label(_("Loading Policy... It may take time. Do not close window!"))
        self.mLabel = label
        self.vbox.pack_start(label, False, False,0)

        expander = gtk.Expander(_("Detail"))
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

