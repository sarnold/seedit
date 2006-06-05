#!/usr/bin/python


import pygtk
pygtk.require('2.0')
import gtk
import sys
import gettext
sys.path.insert(0,"/usr/lib")
from  seedit.GUICommon import *
from  seedit.UILogic import *


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
        self.doCommand("/usr/bin/seedit-unconfined -e", self.mWorkingResult)
        self.doCommand("/usr/bin/seedit-unconfined -n", self.mNetResult)

    def initTextView(self):
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        textbuffer = textview.get_buffer()
        sw.add(textview)
        return (sw,textbuffer)
    
    def doCommand(self, command, textbuffer):
        input = os.popen(command, "r")
        lines = input.readlines()
        string =""
        for line in lines:
            string = string + line

        textbuffer.set_text(string)
        
    
    def __init__(self,parent):
        vbox = gtk.VBox()
        self.mParentWindow=parent
        self.mElement = vbox
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        vbox.pack_start(notebook)
        (tab1, buffer1) = self.initTextView()
        label = gtk.Label(_("Working process"))
        notebook.append_page(tab1, label)
        label = gtk.Label(_("Network process"))
        (tab2,buffer2) = self.initTextView()
        notebook.append_page(tab2, label)

        button = gtk.Button(_("Refresh"))
        button.connect("clicked", self.refreshButtonCallBack)
        hbox = gtk.HBox()
        hbox.pack_start(button,False,False)
        vbox.pack_start(hbox,False,False)
        self.mWorkingResult = buffer1
        self.mNetResult = buffer2
        self.doCommand("/usr/bin/seedit-unconfined -e", self.mWorkingResult)
        self.doCommand("/usr/bin/seedit-unconfined -n", self.mNetResult)

class seeditStatusWindow(seeditCommon):
        
    def __init__(self):
        
        
        # Create the toplevel window
        window = gtk.Window()
        self.mWindow = window
        window.set_title(_("seedit Status"))
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
    seeditStatusWindow()

    gtk.main()
