#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk
import sys
import gettext


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
