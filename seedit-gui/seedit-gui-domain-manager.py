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
sys.path.insert(0,"/usr/lib")
from  seedit.ui.GUICommon import *
from  seedit.ui.UILogic import *
from  seedit.unconfined import *

class deleteDomainTab(seeditCommon):
    
    def radioCallBack(self, widget, data):
        if widget.get_active() == 1:
            self.mTemporalFlag= data

    def updateComboBoxes(self):
        combo = self.mDomainListComboBox 
        model = combo.get_model()
        model.clear()
        domainList = getDeletableDomainList()
        for domain in domainList:
            combo.append_text(domain)       

        combo = self.mDisabledDomainListComboBox
        model = combo.get_model()
        model.clear()
        domainList = getDisableTransDomain()
        for domain in domainList:
            combo.append_text(domain)

        self.mPropertyLabel.set_text("")
        self.mPropertyLabel2.set_text("")

    def deleteButtonCallBack(self, widget, data=None):
        domain = self.get_active_text(self.mDomainListComboBox)


        if self.mTemporalFlag == False:
            message =_("Really remove %s?  The backup is created in extras directory. ") % (domain)
            response = self.showYesNoDialog(message)
            if response == gtk.RESPONSE_NO:
                self.showMessageDialog(gtk.MESSAGE_INFO, _("Operation cancelled.\n"))
                return
        
        r = deleteDomain(domain, self.mTemporalFlag)        
        if r == SEEDIT_SUCCESS:
            self.showMessageDialog(gtk.MESSAGE_INFO, _("Domain removed,next load policy.\n"))
            self.updateComboBoxes()
            if self.mTemporalFlag == False:
                ld=loadPolicyDialog(self.mParentWindow)
                (s, data) = ld.do()
    
    
    def enableButtonCallBack(self, widget, data=None):
        domain = self.get_active_text(self.mDisabledDomainListComboBox)
        r = setDisableTransBoolean(domain, "off")
        if r == SEEDIT_SUCCESS:
            self.showMessageDialog(gtk.MESSAGE_INFO, _("Success.\n"))
            self.updateComboBoxes()
        else:
            self.showMessageDialog(gtk.MESSAGE_INFO, _("Error.\n"))


    def domainListComboCallBack(self,widget,data=None):
        domain = self.get_active_text(widget)
        pList = []

        if domain == "":
            return 
        (pList, confinedFlag) = getDomainProperty(domain)

        str =""
        if confinedFlag == False:
            str = _("Unconfined Domain\n")
        str = str + _("Related Programs:")
        
        for p in pList:
            str = str + p +" "
        self.mPropertyLabel.set_text(str)

    def disabledDomainListComboCallBack(self,widget,data=None):
        domain = self.get_active_text(widget)
        pList = []

        if domain == "":
            return 
        (pList, confinedFlag) = getDomainProperty(domain)

        str =""
        if confinedFlag == False:
            str = _("Unconfined Domain\n")
        str = str + _("Related Programs:")
        
        for p in pList:
            str = str + p +" "
        self.mPropertyLabel2.set_text(str)


        
    def __init__(self,parent):
        
        vboxFrame = gtk.VBox()
        vboxFrame.set_border_width(10)
        self.mParentWindow=parent
        self.mElement = vboxFrame

        ###Delete Domain Frame
        frame = gtk.Frame(_("Delete Domain"))
        vboxFrame.pack_start(frame, False, False,5)
        vbox = gtk.VBox()
        frame.add(vbox)
        
        hbox = gtk.HBox()
        label = gtk.Label(_("Select:"))
        hbox.pack_start(label, False, False,5)
        combo = gtk.combo_box_new_text()
        self.mDomainListComboBox = combo
        domainList = getDeletableDomainList()
        for domain in domainList:
            combo.append_text(domain)
        combo.connect('changed', self.domainListComboCallBack)

        hbox.pack_start(combo,False,False,5)
        vbox.pack_start(hbox, False, False,5)
        expander = gtk.Expander(_("Property"))
        vbox.pack_start(expander, False, False, 0)
        label = gtk.Label("") #Whether unconfined domain, confined programs
        self.mPropertyLabel = label
        expander.add(label)
        
        hbox = gtk.HBox()
        radio = gtk.RadioButton(None, _("Temporally"))
        self.mTemporalFlag = True
        radio.connect("toggled", self.radioCallBack, True)
        radio.set_active(True)
        hbox.pack_start(radio, False, False,5)
        radio = gtk.RadioButton(radio, _("Permanentlly"))
        radio.connect("toggled", self.radioCallBack, False)        
        hbox.pack_start(radio, False, False,5)
        vbox.pack_start(hbox, False, False,5)

        hbox = gtk.HBox()
        button = gtk.Button(_("Apply"))
        button.connect("clicked", self.deleteButtonCallBack)
        hbox.pack_start(button, False, False,5)
        vbox.pack_start(hbox, False, False,5)
      

        ###Enable temporally disabled domain frame
        frame = gtk.Frame(_("Enable temporally disabled domain"))
        vboxFrame.pack_start(frame, False, False,5)
        vbox = gtk.VBox()
        frame.add(vbox)
        
        hbox = gtk.HBox()
        label = gtk.Label(_("Select:"))
        hbox.pack_start(label, False, False,5)
        combo = gtk.combo_box_new_text()
        self.mDisabledDomainListComboBox = combo
        combo.connect('changed', self.disabledDomainListComboCallBack)
        domainList = getDisableTransDomain()
        for domain in domainList:
            combo.append_text(domain)
        hbox.pack_start(combo, False, False,5)
        vbox.pack_start(hbox, False, False,5)
        expander = gtk.Expander(_("Property"))
        vbox.pack_start(expander, False, False, 0)
        label = gtk.Label("") #Whether unconfined domain, confined programs
        self.mPropertyLabel2 = label
        expander.add(label)
        hbox = gtk.HBox()
        button = gtk.Button(_("Apply"))
        button.connect("clicked", self.enableButtonCallBack)
        hbox.pack_start(button, False, False,5)
        vbox.pack_start(hbox, False, False,5)
        

class createDomainTab(seeditCommon):
    
    def daemonRadioCallBack(self,widget, data):
        if widget.get_active() == 1:
            self.mDaemonFlag = data

    def authRadioCallBack(self, widget, data):
        if widget.get_active() == 1:
            self.mAuthFlag = data
    def desktopRadioCallBack(self, widget, data):
        if widget.get_active() == 1:
            self.mDesktopFlag = data
            
    def autoDomainName(self, filename):
        index = filename.rindex("/")
        domain = filename[index+1:] +"_t"
        domain = re.sub("\W","_", domain)
                       
        return domain
    
    def browseButtonCallBack(self, data=None):
        dialog = fileSelectionDialog()

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.getSelected()
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

        extraDomains = getExtraDomainList()
        if domain in extraDomains:
            message = _("Domain template already exists in extras directory. Do you want to reuse?")
            response = self.showYesNoDialog(message)
            if response == gtk.RESPONSE_YES:
                filename = getExtraDomainFileName(domain)
                string = fileString(filename)
            else:
                string = createDomainTemplate(program, domain, parentDomain, self.mDaemonFlag, self.mAuthFlag, self.mDesktopFlag)
            
        else:
            string = createDomainTemplate(program, domain, parentDomain, self.mDaemonFlag, self.mAuthFlag, self.mDesktopFlag)
        if  string != None:
            self.mTextBuffer.set_text(string)
            
            self.mToBeSavedFile= gSPPath+domain+".sp"
            self.mToBeSavedFileLabel.set_label(self.mToBeSavedFile)

    def addButtonCallBack(self,data=None):
        window = insertPolicyWindow(self,self.mTextBuffer)

        
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

        ld=loadPolicyDialog(self.mParentWindow)
        (s, data) = ld.do()

        if s<0:
            os.unlink(filename)
            self.showMessageDialog(gtk.MESSAGE_INFO, _("Syntax error was found.\n"))


            return
        else:

            self.showMessageDialog(gtk.MESSAGE_INFO, _("Domain created successfully.\n"))
               
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
        
        self.mDesktopFlag = False
        hbox = self.yesNoSelection(_("Desktop application?"), self.mDesktopFlag, self.desktopRadioCallBack)
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
        label = gtk.Label("")
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
        button = gtk.Button(_("Add policy"))
        hbox.pack_start(button, False, False, 5)
        button.connect("clicked", self.addButtonCallBack)
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
       
        tab1 = createDomainTab(self)
        label = gtk.Label(_("Create Domain"))
        notebook.append_page(tab1.mElement, label)
        label = gtk.Label(_("Delete Domain"))
        tab2 = deleteDomainTab(self)
        notebook.append_page(tab2.mElement, label)
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
  
    seeditDomainManageWindow()
    gtk.gdk.threads_init()

    gtk.main()


