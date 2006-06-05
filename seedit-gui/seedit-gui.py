#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import gettext
from  seedit.GUICommon import *

GUI_STATUS=1
GUI_MANAGE=2
GUI_ADD=3
GUI_EDIT=4
gVersion = "2.0.0 b4"
gIconPath= "/usr/share/icons/seedit/"
if not os.path.exists(gIconPath+"icon.png"):
    gIconPath="./icons/"
STATUS_COMMAND="./seedit-gui-status.py"

        
class seeditMainWindow(seeditCommon):
    ui = '''<ui>
    <menubar name="MenuBar">
      <menu action="Help">
        <menuitem action="About"/>
      </menu>
      
    </menubar>
    </ui>'''

    def forkProgram(self,path):
        pid = os.fork()
        if(pid==0):
            os.system(path)
            sys.exit(0)
        
    
    def launchGUI(self, mode):

        if(mode == GUI_STATUS):
            self.forkProgram(STATUS_COMMAND)
        else:
            self.showNotImplementedDialog()
        

    def showAbout(self,data=None):
        message = _("SELinux Policy Editor Control Panel\nVersion %s\n") % (gVersion) 
        message += _("All rights reserved (c) 2006 Yuichi Nakamura\n")
        message += _("This software is distributed under GPL.\n")
        message += _("For more information, visit http://seedit.sourceforge.net/\n")
        self.showMessageDialog(gtk.MESSAGE_INFO,message)
    
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
        
        model.append([_("Manage Domain/Role"), newIcon,GUI_MANAGE])
        model.append([_("Add policy"), defaultIcon,GUI_ADD])
        model.append([_("Edit policy"), defaultIcon,GUI_EDIT])

        self.iconView = gtk.IconView(model)
        self.iconView.set_text_column(0)
        self.iconView.set_pixbuf_column(1)
        self.iconView.set_orientation(gtk.ORIENTATION_VERTICAL)
        self.iconView.set_selection_mode(gtk.SELECTION_SINGLE)
        self.iconView.set_columns(-1)
        self.iconView.set_item_width(72)
        self.iconView.connect('item-activated', self.onActive, model)

        frame.add(self.iconView)
        
        label = gtk.Label(_(""))        
        vbox.pack_end(label,False,False)
        window.show_all()

     

           
                


if __name__ == '__main__':
    gettext.install("seedit-gui","/usr/share/locale")
    seeditMainWindow()

    gtk.main()

    
