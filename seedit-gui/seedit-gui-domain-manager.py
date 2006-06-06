#!/usr/bin/python
#All Rights Reserved (C) 2006, Yuichi Nakmura himainu-ynakam@miomio.jp


import pygtk
pygtk.require('2.0')
import gtk
import gobject
import sys
import gettext
import string
sys.path.insert(0,"/usr/lib")
from  seedit.ui.GUICommon import *
from  seedit.ui.UILogic import *
from  seedit.unconfined import *

class seStatusTab(seeditCommon):
    def comboCallBack(self,combobox, data=None):
        model = combobox.get_model()
        index = combobox.get_active()
        print index
        
    def applyButtonCallBack(self,widget, data=None):
        index = self.mCurrentModeComboBox.get_active()
        if index == 0:
            currentMode = ENFORCING
        elif index ==1:
            currentMode = PERMISSIVE
        else:
            currentMode = DISABLED
        
        index = self.mBootModeComboBox.get_active()
        if index == 0:
            bootMode = ENFORCING
        elif index ==1:
            bootMode = PERMISSIVE
        else:
            bootMode = DISABLED
        
        result = setMode(currentMode)
        if result == SEEDIT_ERROR:
            message = _("Failed to change current mode. Permission denied")
            self.showMessageDialog(gtk.MESSAGE_ERROR,message)
            mode = getMode()
            self.setModeCombo(self.mCurrentModeComboBox,mode)
        
        result = setBootMode(bootMode)
        if result == SEEDIT_ERROR:
            message = _("Failed to change boot mode. Permission denied")
            self.showMessageDialog(gtk.MESSAGE_ERROR,message)
            mode = getBootMode()
            self.setModeCombo(self.mBootModeComboBox,mode)

        
    def setModeCombo(self, combo, mode):

        if mode == PERMISSIVE:
            combo.set_active(1)
        elif mode == ENFORCING:
            combo.set_active(0)
        else:        
            combo.set_active(2)
    
    def __init__(self,parent):
        vbox = gtk.VBox()
        self.mParentWindow=parent
        self.mElement = vbox

        label = gtk.Label(_("seedit Installed?"))
        hbox = gtk.HBox()
        hbox.pack_start(label, False, False,10)
        vbox.pack_start(hbox, False, False)
        if seeditInstalled()==True:
            label = gtk.Label(_("Yes"))
        else:
            label = gtk.Label(_("No!"))
        hbox.pack_start(label, False, False,10)

        
        label = gtk.Label(_("Current mode:"))
        hbox1=gtk.HBox()
        hbox1.pack_start(label,False,False,10)
        combo = gtk.combo_box_new_text()
        self.mCurrentModeComboBox = combo
        hbox1.pack_start(combo,False,False,10)
        combo.append_text(_("Enforcing"))
        combo.append_text(_("Permissive"))
        combo.append_text(_("Disabled"))

        mode = getMode()
        self.setModeCombo(self.mCurrentModeComboBox,mode)
        vbox.pack_start(hbox1,False,False)
        
        
        label = gtk.Label(_("Mode at boot:"))
        hbox1=gtk.HBox()
        hbox1.pack_start(label,False,False,10)
        combo = gtk.combo_box_new_text()
        self.mBootModeComboBox = combo
        hbox1.pack_start(combo,False,False,10)
        combo.append_text(_("Enforcing"))
        combo.append_text(_("Permissive"))
        combo.append_text(_("Disabled"))

        mode = getBootMode()
        self.setModeCombo(combo,mode)
        vbox.pack_start(hbox1,False,False)
        separator = gtk.HSeparator() 
        vbox.pack_start(separator,False,False,5)
        
        button = gtk.Button(_("Apply"))
        button.connect("clicked", self.applyButtonCallBack)
        hbox = gtk.HBox()
        hbox.pack_start(button,False,False)
        vbox.pack_start(hbox,False,False)
        
        
class processStatusTab(seeditCommon):
    
    
    def refreshButtonCallBack(self,widget, data=None):
        self.mWorkingListStore.clear()
        self.mNetworkListStore.clear()
        list = getWorkingProcessList(gUnconfinedDomains)
        for l in list:
           self.mWorkingListStore.append(l)
        list = getNetworkProcessList(gUnconfinedDomains)
        for l in list:
            self.mNetworkListStore.append(l)
        

    def initModel(self, data):
        lstore = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING)

        for item in data:
            lstore.append(data)
        return lstore

    #From demo pygtk 2.0
    def addColumns(self, treeview, header):
        model = treeview.get_model()
        

        renderer = gtk.CellRendererToggle()

        column = gtk.TreeViewColumn(header[0], gtk.CellRendererText(),
                                    text=0)
        column.set_sort_column_id(0)
        treeview.append_column(column)


        column = gtk.TreeViewColumn(header[1], gtk.CellRendererText(),
                                    text=1)
        column.set_sort_column_id(1)
        treeview.append_column(column)
        column = gtk.TreeViewColumn(header[2], gtk.CellRendererText(),
                                     text=2)
        column.set_sort_column_id(2)
        treeview.append_column(column)
        
    def initTreeView(self,model,header):
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_size_request(400,300)

        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        treeview = gtk.TreeView(model)
        treeview.set_rules_hint(True)
        treeview.set_search_column(2)
        sw.add(treeview)
        self.addColumns(treeview,header)
        return sw


    
    def __init__(self,parent):
        self.mWorkingListStore = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING)
        self.mNetworkListStore = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING)
        
        list = getWorkingProcessList(gUnconfinedDomains)
        for l in list:
           self.mWorkingListStore.append(l)
        list = getNetworkProcessList(gUnconfinedDomains)
        for l in list:
            self.mNetworkListStore.append(l)

        
        vbox = gtk.VBox()
        self.mParentWindow=parent
        self.mElement = vbox
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        vbox.pack_start(notebook)
        header = (_("PID"),_("Process"),_("Domain"))
        tab1 = self.initTreeView(self.mWorkingListStore,header)
        label = gtk.Label(_("Working process"))
        notebook.append_page(tab1, label)
        label = gtk.Label(_("Network process"))
        header = (_("Port"),_("Process"),_("Domain"))
        tab2  = self.initTreeView(self.mNetworkListStore,header)
        notebook.append_page(tab2, label)

        button = gtk.Button(_("Refresh"))
        button.connect("clicked", self.refreshButtonCallBack)
        hbox = gtk.HBox()
        hbox.pack_start(button,False,False)
        vbox.pack_start(hbox,False,False)

      

class seeditDomainManageWindow(seeditCommon):
        
    def __init__(self):
        
        
        # Create the toplevel window
        window = gtk.Window()
        self.mWindow = window
        window.set_title(_("seedit Domain/Role Manager"))
        
        window.connect('destroy', lambda w: gtk.main_quit())

        vbox = gtk.VBox()
        window.add(vbox)

        menubar = self.initMenu(window)
        vbox.pack_start(menubar, False)
             
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        vbox.pack_start(notebook)

        tab1 = seStatusTab(self.mWindow)
        label = gtk.Label(_("SELinux"))
        notebook.append_page(tab1.mElement, label)
        label = gtk.Label(_("Process"))
        tab2 = processStatusTab(self.mWindow)
        notebook.append_page(tab2.mElement, label)
        label = gtk.Label("")
        vbox.pack_end(label)
        window.show_all()
        
        return
 

    def quitCallBack(self, b):
        print 'Quitting program'
        gtk.main_quit()



if __name__ == '__main__':
    gettext.install("seedit-gui","/usr/share/locale")
  
    seeditDomainManageWindow()

    gtk.main()
