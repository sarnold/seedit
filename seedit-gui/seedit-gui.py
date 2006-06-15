#!/usr/bin/python
#All Rights Reserved (C) 2006, Yuichi Nakmura himainu-ynakam@miomio.jp

import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import gettext
sys.path.insert(0,"/usr/lib")
from  seedit.ui.GUICommon import *
from seedit.ui.UILogic import *

GUI_STATUS=1
GUI_MANAGE=2
GUI_GENERATE=3
GUI_EDIT=4
GUI_LOAD=5
gIconPath= "/usr/share/icons/seedit/"
if not os.path.exists(gIconPath+"icon.png"):
    gIconPath="./icons/"
STATUS_COMMAND="/usr/sbin//seedit-gui-status"
DOMAIN_MANAGE_COMMAND="/usr/sbin/seedit-gui-domain-manager"

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
        model.append([_("Generate policy"), defaultIcon,GUI_GENERATE])
        model.append([_("Edit policy"), defaultIcon,GUI_EDIT])
        model.append([_("Apply policy/Relabel"), defaultIcon,GUI_LOAD])

        self.iconView = gtk.IconView(model)
        self.iconView.set_text_column(0)
        self.iconView.set_pixbuf_column(1)
        self.iconView.set_orientation(gtk.ORIENTATION_VERTICAL)
        self.iconView.set_selection_mode(gtk.SELECTION_SINGLE)
        self.iconView.set_columns(-1)
#        self.iconView.set_item_width(70)
        self.iconView.connect('item-activated', self.onActive, model)

        frame.add(self.iconView)
        
        label = gtk.Label("")        
        vbox.pack_end(label,False,False)
        window.show_all()

     

           
                


if __name__ == '__main__':
    gettext.install("seedit-gui","/usr/share/locale")
    seeditMainWindow()

    gtk.main()

    
