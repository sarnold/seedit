#!/usr/bin/python
#All Rights Reserved (C) 2006, Yuichi Nakmura himainu-ynakam@miomio.jp


import pygtk
pygtk.require('2.0')
import gtk
import gobject
import sys
import gettext
import string
import re
sys.path.insert(0,"/usr/lib")
from  seedit.ui.GUICommon import *
from  seedit.ui.UILogic import *
from  seedit.unconfined import *

class createDomainTab(seeditCommon):
    
    def daemonRadioCallBack(self,widget, data):
        if widget.get_active() == 1:
            self.mDaemonFlag = data

    def authRadioCallBack(self, widget, data):
        if widget.get_active() == 1:
            self.mAuthFlag = data
            
    def autoDomainName(self, filename):
        index = filename.rindex("/")
        domain = filename[index+1:] +"_t"
        domain = re.sub("\W","_", domain)
                       
        return domain
    
    def browseButtonCallBack(self, data=None):
        dialog = gtk.FileChooserDialog(_("Choose Program"),
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name(_("All files"))
        filter.add_pattern("*")
        dialog.add_filter(filter)
       
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            filename = os.path.realpath(filename)
            self.mProgramEntry.set_text(filename)
            domain = self.autoDomainName(filename)
            self.mDomainEntry.set_text(domain)
        elif response == gtk.RESPONSE_CANCEL:
            pass
       
        dialog.destroy()

        
    def createButtonCallBack(self, data=None):
        program = self.mProgramEntry.get_text()
        domain = self.mDomainEntry.get_text()
        parentDomain = self.mParentDomainEntry.get_text()
        string = createDomainTemplate(program, domain, parentDomain, self.mDaemonFlag, self.mAuthFlag)
        if  string != None:
            self.mTextBuffer.set_text(string)
            
            self.mToBeSavedFile= gSPPath+domain+".sp"
            self.mToBeSavedFileLabel.set_label(self.mToBeSavedFile)
        
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

        ld = loadPolicyDialog(self.mParentWindow)
        r = 0

        r = loadPolicy()

        if r < 0:
            self.showMessageDialog(gtk.MESSAGE_INFO, _("Syntax error is found. Save cancelled.\n"))
            os.unlink(filename)
            ld.loadPolicy()
            return
        return


        
        s = createDomain(data,filename)

        
        if s == SEEDIT_ERROR_SEEDIT_LOAD:
            self.showMessageDialog(gtk.MESSAGE_INFO, _("Syntax error is found. Save cancelled.\n"))
            return
        elif s == SEEDIT_ERROR_FILE_WRITE:
            self.showMessageDialog(gtk.MESSAGE_INFO, _("File write error. Save cancelled.\n"))
            return
        elif s == SEEDIT_SUCCESS:
            self.showMessageDialog(gtk.MESSAGE_INFO, _("Success.\n"))
            return
        
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
    
    def __init__(self,parent):
        
        vboxFrame = gtk.VBox()
        vboxFrame.set_border_width(10)
        self.mParentWindow=parent
        self.mElement = vboxFrame
        
        frame = gtk.Frame(_("Domain information"))
        vboxFrame.pack_start(frame, False, False,5)
        
        vbox = gtk.VBox()
        frame.add(vbox)
        label = gtk.Label(_("Program you want to confine:"))
        hbox = gtk.HBox()
        hbox.pack_start(label, False, False,5)
        vbox.pack_start(hbox, False, False)
        entry = gtk.Entry()
        entry.set_max_length(100)        
        hbox.pack_start(entry,False, False,5)
        button = gtk.Button(_("Browse"))
        button.connect("clicked", self.browseButtonCallBack)
        hbox.pack_start(button, False, False, 5)
        self.mProgramEntry = entry
        
        label = gtk.Label(_("Name of domain:"))
        hbox = gtk.HBox()
        hbox.pack_start(label, False, False,5)
        entry = gtk.Entry()
        entry.set_max_length(50)
        hbox.pack_start(entry,False, False,5)
        self.mDomainEntry = entry
        vbox.pack_start(hbox, False, False)
        
        # Create the expander
        expander = gtk.Expander(_("Optional"))
        vbox.pack_start(expander, False, False, 0)
        # The Label for the expander
        label = gtk.Label(_("Parent Domain"))
        hbox = gtk.HBox()
        hbox.pack_start(label, False, False,5)
        entry = gtk.Entry()
        entry.set_max_length(100)
        self.mParentDomainEntry = entry
        hbox.pack_start(entry,False, False,5)
        expander.add(hbox)

        self.mDaemonFlag= True
        hbox = self.yesNoSelection(_("Daemon program?"), self.mDaemonFlag, self.daemonRadioCallBack)
        vbox.pack_start(hbox, False, False, 0)

        self.mAuthFlag = False
        hbox = self.yesNoSelection(_("Authentication program?"), self.mAuthFlag, self.authRadioCallBack)
        vbox.pack_start(hbox, False, False, 0)

        hbox = gtk.HBox()
        button = gtk.Button(_("Create Template"))
        hbox.pack_start(button, False, False, 5)
        button.connect("clicked", self.createButtonCallBack)
        vbox.pack_start(hbox, False, False, 5)
        


        frame = gtk.Frame(_("Created template"))
        vboxFrame.pack_start(frame, False, False, 5)
        vbox = gtk.VBox()
        frame.add(vbox)
        hbox = gtk.HBox()
        label = gtk.Label(_("Will be saved to:"))
        hbox.pack_start(label,False,False,5)
        label = gtk.Label(_(""))
        self.mToBeSavedFileLabel= label
        self.mToBeSavedFile=None
        
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
        button = gtk.Button(_("Save and Apply"))
        hbox.pack_start(button, False, False, 5)
        button.connect("clicked", self.saveButtonCallBack)
        vbox.pack_start(hbox, False, False, 5)
        


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
       
        tab1 = createDomainTab(self.mWindow)
        label = gtk.Label(_("Create Domain"))
        notebook.append_page(tab1.mElement, label)
        label = gtk.Label(_("Create Role"))
#        tab2 = processStatusTab(self.mWindow)
#        notebook.append_page(tab2.mElement, label)
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
