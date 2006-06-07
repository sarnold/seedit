#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk
import os
import sys
import gettext
import time
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

    mVersion = "2.0.0 b4"
    
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

  

'''
Dialog that shows progress of seedit-load
'''
class loadPolicyDialog(gtk.Dialog):

    def close(self):
        self.destroy()
    def doCommand(self,command):
        input=os.popen(command, "r")
        line = input.readline()
        while line:
            sys.stdout.write(line)
            sys.stdout.flush()
            input.flush()
            self.mTextBuffer.insert(self.mTextBuffer.get_end_iter(),line)
            line = input.readline()
        
        if input.close():
            return SEEDIT_ERROR_SEEDIT_LOAD
    
        return SEEDIT_SUCCESS
    
    def loadPolicy(self):
        command = gSeedit_load+" -v"
        status = self.doCommand(command)
#        self.destroy()
        return status


    def __init__(self,parent):
        gtk.Dialog.__init__(self,_("load policy"),parent, gtk.DIALOG_MODAL)

        label= gtk.Label(_("Loading Policy... It may take time"))
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
        
        self.show_all()
        ####Thread here!
        pid = os.fork()
        if pid ==0:
            self.loadPolicy()
            self.response(1)
            self.destroy()
            sys.exit(0)
        self.run()


        
