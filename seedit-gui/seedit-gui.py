#!/usr/bin/python

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
import sys
import os
import gettext
import gobject
sys.path.insert(0,"/usr/lib")
from  seedit.ui.GUICommon import *
from seedit.ui.UILogic import *

GUI_STATUS=1
GUI_MANAGE=2
GUI_GENERATE=3
GUI_EDIT=4
GUI_LOAD=5
GUI_RMANAGE=6
gIconPath= "/usr/share/icons/seedit/"
if not os.path.exists(gIconPath+"icon.png"):
    gIconPath="./icons/"
STATUS_COMMAND="/usr/sbin//seedit-gui-status"
DOMAIN_MANAGE_COMMAND="/usr/sbin/seedit-gui-domain-manager"
ROLE_MANAGE_COMMAND="/usr/sbin/seedit-gui-role-manager"

GENERATE_COMMAND="/usr/sbin/seedit-gui-generate-policy"
EDIT_COMMAND="/usr/sbin/seedit-gui-edit"
LOAD_COMMAND="/usr/sbin/seedit-gui-load"

class seeditMainWindow(seeditCommon):

    def forkProgram(self,path):
        pid = os.fork()
        if(pid==0):
            os.system(path)
            sys.exit(0)
        
    
    def launchGUI(self, mode):

        if(mode == GUI_STATUS):
            self.forkProgram(STATUS_COMMAND)
        elif(mode == GUI_MANAGE):
            self.forkProgram(DOMAIN_MANAGE_COMMAND)
        elif(mode == GUI_RMANAGE):
            self.forkProgram(ROLE_MANAGE_COMMAND)
        elif(mode == GUI_GENERATE):
            self.forkProgram(GENERATE_COMMAND)
	elif(mode == GUI_EDIT):
            self.forkProgram(EDIT_COMMAND)
        elif(mode == GUI_LOAD):
            self.forkProgram(LOAD_COMMAND)
        else:
            self.showNotImplementedDialog()
    
    def onActive(self, iconView, path,model=None):
        selected = iconView.get_selected_items()
        if len(selected) == 0: return
        i = selected[0][0]
        mode = model[i][2]
        self.launchGUI(mode)

    def onButtonClick(self,button, mode):
        
        self.launchGUI(mode)
        
    def __init__(self):
        window = gtk.Window()
        window.set_title(_("SELinux Policy Editor Control Panel"))
        window.connect('destroy', lambda w: gtk.main_quit())
        vbox = gtk.VBox()
        window.add(vbox)
     
        menubar = self.initMenu(window)
        vbox.pack_start(menubar, False)

        
        frame = gtk.Frame("")
        frame.set_border_width(10)
        frame.set_size_request(400, 300)
        vbox.pack_start(frame)
        model = gtk.ListStore(str, gtk.gdk.Pixbuf,int)

      
        defaultIcon = gtk.gdk.pixbuf_new_from_file(gIconPath+"icon.png")
        newIcon = gtk.gdk.pixbuf_new_from_file(gIconPath+"new.png")
        delIcon = gtk.gdk.pixbuf_new_from_file(gIconPath+"del.png")
        
        model.append([_("Status"), defaultIcon,GUI_STATUS])
        
        model.append([_("Manage Domain"), newIcon,GUI_MANAGE])

        rbac = getRBAC()
        if rbac:
            model.append([_("Manage Role"), newIcon,GUI_RMANAGE])
        
        model.append([_("Generate policy"), defaultIcon,GUI_GENERATE])
        model.append([_("Edit policy"), defaultIcon,GUI_EDIT])
        model.append([_("Apply policy/Relabel"), defaultIcon,GUI_LOAD])

        noIconViewFlag=False #in old pygtk, no IconView widget
        try:
            self.iconView = gtk.IconView(model)
        except:
            noIconViewFlag = True

        if noIconViewFlag == False:
            self.iconView.set_text_column(0)
            self.iconView.set_pixbuf_column(1)
            self.iconView.set_orientation(gtk.ORIENTATION_VERTICAL)
            self.iconView.set_selection_mode(gtk.SELECTION_SINGLE)
            self.iconView.set_columns(-1)
            self.iconView.connect('item-activated', self.onActive, model)

            frame.add(self.iconView)
        else:
            #No iconview, use vbox
            vbox= gtk.VBox()
            frame.add(vbox)
            for row in model:
                button = gtk.Button(row[0])
                vbox.pack_start(button,False)
                button.connect('clicked',self.onButtonClick,row[2])
            
        label = gtk.Label("")        
        vbox.pack_end(label,False,False)
        window.show_all()

     

           
                


if __name__ == '__main__':
    gettext.install("seedit-gui","/usr/share/locale")
    seeditMainWindow()

    gtk.main()

    
