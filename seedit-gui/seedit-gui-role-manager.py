#!/usr/bin/python -u

#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura
#! 
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
import gtk.gdk
import gobject
import sys
import gettext
import string
import re
from  seedit.ui.GUICommon import *
from  seedit.ui.UILogic import *
from  seedit.unconfined import *

class createUserTab(seeditCommon):
    
    def remoteLoginRadioCallBack(self,widget, data):
        if widget.get_active() == 1:
            self.mRemoteLoginFlag = data

    def dacSkipRadioCallBack(self, widget, data):
        if widget.get_active() == 1:
            self.mDacSkipFlag = data
            
    def autoDomainName(self, filename):
        index = filename.rindex("/")
        domain = filename[index+1:] +"_t"
        domain = re.sub("\W","_", domain)
                       
        return domain
    


        
    def createButtonCallBack(self, data=None):
        user = self.mUserEntry.get_text()
        role = self.mRoleEntry.get_text()

        string = createRoleTemplate(user, role, self.mRemoteLoginFlag, self.mDacSkipFlag)
            
        
        if  string != None:
            self.mEditFrame.mTextBuffer.set_text(string)
            
            self.mEditFrame.mToBeSavedFile= gSPPath+role+".sp"
            self.mEditFrame.mToBeSavedFileLabel.set_label(self.mEditFrame.mToBeSavedFile)
   
 
    
    def __init__(self,parent):
        
        vboxFrame = gtk.VBox()
        vboxFrame.set_border_width(10)
        self.mParentWindow=parent
        self.mElement = vboxFrame
        
        frame = gtk.Frame(_("Role information"))
        vboxFrame.pack_start(frame, False, False,5)
        
        vbox = gtk.VBox()
        frame.add(vbox)
        
        label = gtk.Label(_("Role name"))
        hbox = gtk.HBox()
        hbox.pack_start(label, False, False,5)
        entry = gtk.Entry()
        entry.set_max_length(50)
        hbox.pack_start(entry,False, False,5)
        self.mRoleEntry = entry
        vbox.pack_start(hbox, False, False)
        
        label = gtk.Label(_("User name"))
        hbox = gtk.HBox()
        hbox.pack_start(label, False, False,5)
        entry = gtk.Entry()
        entry.set_max_length(100)        
        hbox.pack_start(entry,False, False,5)
        self.mUserEntry = entry
        vbox.pack_start(hbox, False, False)

        self.mRemoteLoginFlag= True
        hbox = self.yesNoSelection(_("Remote login allowed?"), self.mRemoteLoginFlag, self.remoteLoginRadioCallBack)
        vbox.pack_start(hbox, False, False, 0)

        self.mDacSkipFlag = False
        hbox = self.yesNoSelection(_("Skip DAC check?"), self.mDacSkipFlag, self.dacSkipRadioCallBack)
        vbox.pack_start(hbox, False, False, 0)

        hbox = gtk.HBox()
        button = gtk.Button(_("Create Template"))
        hbox.pack_start(button, False, False, 5)
        button.connect("clicked", self.createButtonCallBack)
        vbox.pack_start(hbox, False, False, 5)

        frame = editTemplateFrame(self.mParentWindow,_("Created template"), _("Will be saved to:"))
        self.mEditFrame=frame
        vboxFrame.pack_start(frame.mFrame, False, False, 5)
     


class seeditRoleManageWindow(seeditCommon):
        
    def __init__(self):
        
        
        # Create the toplevel window
        window = gtk.Window()
        self.mWindow = window
        window.set_title(_("seedit Role Manager"))

        
        window.connect('destroy', lambda w: gtk.main_quit())

        vbox = gtk.VBox()
        window.add(vbox)

        menubar = self.initMenu(window)
        vbox.pack_start(menubar, False)
             
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        vbox.pack_start(notebook)
       
        tab1 = createUserTab(self)
        label = gtk.Label(_("Manage Role"))
        notebook.append_page(tab1.mElement, label)
        label = gtk.Label(_("Assign Role"))
#        tab2 = assignRoleTab(self)
#        notebook.append_page(tab2.mElement, label)
        label = gtk.Label("")
        self.mStatusLabel = label
        vbox.pack_end(label)
        window.show_all()
        
        return
 

    def quitCallBack(self, b):
        print 'Quitting program'
        gtk.main_quit()

if __name__ == '__main__':
    gettext.install("seedit-gui","/usr/share/locale")

    seeditRoleManageWindow()
    gtk.gdk.threads_init()

    gtk.main()


