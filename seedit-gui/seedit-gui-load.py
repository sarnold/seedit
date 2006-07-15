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
import gobject
import sys
import gettext
sys.path.insert(0,"/usr/lib")
from  seedit.ui.GUICommon import *
from  seedit.ui.UILogic import *

class seeditLoadWindow(seeditCommon):
	def radioCallBack(self,widget,data=None):
		if widget.get_active() == 1:
			self.mType=data

	def applyButtonCallBack(self, widget, data=None):
		if self.mType=="load":
			closeFlag = False
			ld=loadPolicyDialog(self,closeFlag)
			(s, data) = ld.do()
			return
		elif self.mType=="init":
			title =_("Initialize label")
			message= _("Relabeling all file labels, it will take very  long time.")
			closeFlag = False
			command = gSeedit_load+" -vi"
			ld=loadPolicyDialog(self,closeFlag,title,message,command)

			(s, data) = ld.do()
		elif self.mType=="restorecon":
			title =_("restorecon")
			message= _("restorecon to file")
			closeFlag = False
			filename = self.mFileEntry.get_text()
			command = gRestorecon+" "+filename+" -Rv"
			ld=loadPolicyDialog(self,closeFlag,title,message,command)
		
			(s, data) = ld.do()
			

	def browseButtonCallBack(self, data=None):
		dialog = fileSelectionDialog()
		r=dialog.run()
		if r ==gtk.RESPONSE_OK:
			selected= dialog.getSelected()
			self.mFileEntry.set_text(selected)
	
	def __init__(self):
		window = gtk.Window()
		self.mWindow = window
		window.set_title(_("seedit load policy/relabel"))
		window.connect('destroy', lambda w: gtk.main_quit())
		frameVbox = gtk.VBox()

		window.add(frameVbox)

		frame = gtk.Frame("")
		frameVbox.pack_start(frame,False)

		vbox = gtk.VBox()
		frame.add(vbox)
		hbox=gtk.HBox()
		vbox.pack_start(hbox,False)
		radio = gtk.RadioButton(None, _("Load policy"))
		radio.connect("toggled", self.radioCallBack, "load")
		self.mType="load"
		hbox.pack_start(radio,False)

		hbox=gtk.HBox()
		vbox.pack_start(hbox,False)
		radio = gtk.RadioButton(radio, _("Initialize all file labels"))
		radio.connect("toggled", self.radioCallBack, "init")
		hbox.pack_start(radio,False)

		hbox=gtk.HBox()
		vbox.pack_start(hbox,False)
		radio = gtk.RadioButton(radio, _("restorecon to file"))
		radio.connect("toggled", self.radioCallBack, "restorecon")
		hbox.pack_start(radio,False)
		entry = gtk.Entry()
		self.mFileEntry=entry
		hbox.pack_start(entry,False)		
		button = gtk.Button(_("Browse"))
		button.connect("clicked", self.browseButtonCallBack)
		hbox.pack_start(button, False, False, 5)

		hbox=gtk.HBox()
		frameVbox.pack_start(hbox,False)
		button = gtk.Button(_("Apply"))
		button.connect("clicked", self.applyButtonCallBack)
		hbox.pack_start(button,False)

	
		window.show_all()

            
if __name__ == '__main__':
	gettext.install("seedit-gui","/usr/share/locale")
	seeditLoadWindow()
	gtk.gdk.threads_init()
	gtk.gdk.threads_enter()
	gtk.main()
	gtk.gdk.threads_leave()
