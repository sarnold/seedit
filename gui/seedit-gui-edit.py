#!/usr/bin/python -u

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
import gobject
import sys
import gettext
from  seedit.ui.GUICommon import *
from  seedit.ui.UILogic import *

class openDomainDialog(gtk.Dialog, seeditCommon):

	def getOpenDomain(self):
		return self.mDomain
	
	
	def domainListComboCallBack(self,widget,data=None):
		self.mDomain= self.get_active_text(widget)

	def openFile(self):
		self.mDomain = self.mEntry.get_text()
		domain = self.mDomain
		if re.search("\.sp$",domain):
			filename = gSPPath +"/"+domain
		else:
			filename = gSPPath +"/"+domain+".sp"
		try:
			input = open(filename,'r')
		except:
			return None
		return input
			

	def show(self):
		r = self.run()
		self.destroy()
		return r
	def __init__(self,parent):
		self.mParentWindow = parent
		gtk.Dialog.__init__(self,_("Open domain"),parent.mWindow, gtk.DIALOG_MODAL,(gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
		hbox = gtk.HBox()
		label = gtk.Label(_("Select domain:"))
		hbox.pack_start(label, False, False,5)
		combo = gtk.combo_box_entry_new_text()
		
		self.mDomainListComboBox = combo
		self.mEntry = combo.child

		self.mDomain=""
		domainList = getEditableDomainList()
		for domain in domainList:
			combo.append_text(domain)
		combo.connect('changed', self.domainListComboCallBack)
		self.vbox.pack_start(combo,False)

		self.show_all()
	


class seeditEditWindow(seeditCommon):
    ui = '''<ui>
    <menubar name="MenuBar">
      <menu action="Help">
        <menuitem action="Manual"/>
        <menuitem action="About"/>
      </menu>
     </menubar>
      <toolbar name="ToolBar">
      <toolitem action="Open"/>
      <separator/>
      <toolitem action="Save"/>
      <separator/>
      <toolitem action="Add"/>
      <separator/>
      <toolitem action="Reload"/>

    </toolbar>
    </ui>'''

    def SaveCallBack(self,data=None):
	    if self.mDomain == "":
		    return
	    buf = self.mTextBuffer
	    start = buf.get_start_iter()
	    end = buf.get_end_iter()
	    str = buf.get_text(start, end)

	    filename = getDomainFileName(self.mDomain)
	    r = saveStringToFile(str,filename)
	    if r != SEEDIT_SUCCESS:
		    self.showMessageDialog(gtk.MESSAGE_ERROR, _("There was an error opening the file:%s. \n")%(filename))

		    return
	    
	    ld=loadPolicyDialog(self)
	    (s, data) = ld.do()
	    if s<0:
		    msg = _("%s:Syntax error in line %s") % (self.mDomain,data)
		    lineno=int(data) -1
		    start =  buf.get_start_iter()
		    start.set_line(lineno)
		    end = buf.get_start_iter()
		    end.set_line(lineno+1)
		    tag = buf.get_tag_table()
		    tag = buf.create_tag(background="red")
		    buf.apply_tag(tag,start,end)
		    r = saveStringToFile(self.mBackupLines, filename)
		    if r != SEEDIT_SUCCESS:
			    self.showMessageDialog(gtk.MESSAGE_ERROR, _("There was an error opening the file:%s. \n")%(filename))

			    return
	    else:
		    msg = _("%s:load success") % (self.mDomain)
		    self.mBackupLines = str
		    
	    self.mStatusLabel.set_text(msg)

    def writeTextView(self, input, domain):
	    lines = input.readlines()
	    self.mBackupLines=""
	    for l in lines:
		    self.mBackupLines = self.mBackupLines + l
	    
	    self.mTextBuffer.delete(self.mTextBuffer.get_start_iter(),self.mTextBuffer.get_end_iter())
	    
	    for line in lines:
		    self.mTextBuffer.insert(self.mTextBuffer.get_end_iter(),line)

	    self.mStatusLabel.set_text(_("Editing %s") % (domain))
	    input.close()
	    

    def OpenCallBack(self,data=None):
	    dialog = openDomainDialog(self)
	    r = dialog.show()
	    if r==gtk.RESPONSE_CANCEL:
		    return
	    input = dialog.openFile()
	    if input ==None:
		    self.showMessageDialog(gtk.MESSAGE_ERROR, _("There was an error opening the file.\n"))

		    
		    return
	    self.mDomain = dialog.getOpenDomain()
	    
	    self.writeTextView(input,self.mDomain)
	    

    def AddCallBack(self,data=None):
	    window = insertPolicyWindow(self,self.mTextBuffer)

    def ReloadCallBack(self,data=None):
	    if self.mDomain == "":
		    return
	    filename = getDomainFileName(self.mDomain)
	    input = open(filename)
	    self.writeTextView(input,self.mDomain)

    def initMenu(self,window):
        uimanager = gtk.UIManager()
	accelgroup = uimanager.get_accel_group()
        window.add_accel_group(accelgroup)
	actiongroup = gtk.ActionGroup('seeditUIManager')
        self.actiongroup = actiongroup
	actiongroup.add_actions([ ('About', gtk.STOCK_DIALOG_INFO,_("_About"), None,
                                  _('About'), self.showAbout),
				  ('Manual', gtk.STOCK_HELP,_("_Help"), None,
                                  _('Manual'), self.showManual),
                                 ('Help', None, _('_Help')),



				  ('Save', gtk.STOCK_SAVE, _("_Save"), None,_("Save and apply"), self.SaveCallBack),
				  ('Open', gtk.STOCK_OPEN, _("_Open"), None,_("Open domain"), self.OpenCallBack),
				  ('Add', gtk.STOCK_ADD, _("_Add"), None,_("Add policy"), self.AddCallBack),
				  ('Reload', gtk.STOCK_REFRESH, _("_Reload"), None,_("Reload"), self.ReloadCallBack)
				  ])
        uimanager.insert_action_group(actiongroup, 0)
        uimanager.add_ui_from_string(self.ui)
	menubar = uimanager.get_widget('/MenuBar')
	toolbar = uimanager.get_widget('/ToolBar')
        return (menubar,toolbar)


    def __init__(self):
        window = gtk.Window()
        self.mWindow = window
	self.mDomain =""
	self.mBackupLines="" # Contents of file before save
        window.set_title(_("seedit policy editor"))
        window.connect('destroy', lambda w: gtk.main_quit())

        vbox = gtk.VBox()
        window.add(vbox)

	(menubar, toolbar)=self.initMenu(self.mWindow)
	vbox.pack_start(menubar,False)
	vbox.pack_start(toolbar,False)

	sw = gtk.ScrolledWindow()
        sw.set_size_request(300,200)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        textbuffer = textview.get_buffer()
        self.mTextBuffer= textbuffer
        sw.add(textview)
	vbox.pack_start(sw,True)

	label=gtk.Label("")
	self.mStatusLabel = label
	vbox.pack_start(label,False)
	window.show_all()
	
            
if __name__ == '__main__':
    gettext.install("seedit","/usr/share/locale")
    seeditEditWindow()
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
