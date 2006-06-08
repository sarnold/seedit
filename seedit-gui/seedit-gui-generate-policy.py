#!/usr/bin/python
#All Rights Reserved (C) 2006, Yuichi Nakmura himainu-ynakam@miomio.jp

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import sys
import gettext
import threading
import time
sys.path.insert(0,"/usr/lib")
from  seedit.ui.GUICommon import *
from  seedit.ui.UILogic import *
from  seedit.audit2spdl import *

	
'''
This thread generate policy and store to mResult 
'''
class generatePolicyThread(threading.Thread):
	def updateLabel(self, data):
		(i,size)=data
		self.mDialog.mProgressLabel.set_text(_("Progress:%d/%d") % (i,size))	

	
	def __init__(self,dialog):
		threading.Thread.__init__(self)
		self.mDialog = dialog
	def run(self):
		self.mDialog.mGenerateButton.set_sensitive(False)

		domdoc=readSPDLSpec(gSpecXML)
		result =[]
		input = open("test.log", 'r')
		lines = readLog(input, True)

		size = len(lines)
		i=0
		for line in lines:
			data = (i,size)
			gobject.idle_add(self.updateLabel, data)
			print i
			rule = parseLine(line)
			if(rule):
				spRuleList=genSPDL(rule,line,domdoc)
				
				list=SPDLstr(spRuleList,line)
				result.append(list)
			i = i+1				     
		data = (i,size)
		gobject.idle_add(self.updateLabel, data)
		self.mDialog.mWindow.emit("done",result)
		self.mDialog.mGenerateButton.set_sensitive(True)


class seeditGeneratePolicyWindow(seeditCommon):
	def generateCallBack(self,widget, data=None):

		thread = generatePolicyThread(self)
		thread.start()

	'''
	When policy generation is done, it is called
	'''
        def doneCallBack(self,widget,data=None):
		print data

        def __init__(self):
		gobject.signal_new("done", gtk.Window,
				   gobject.SIGNAL_RUN_LAST,
				   gobject.TYPE_NONE,
				   (gobject.TYPE_PYOBJECT,))
		window = gtk.Window()
		self.mWindow = window
		self.mResult = []
		window.set_title(_("Policy generater"))
		window.connect('destroy', lambda w: gtk.main_quit())
		vbox = gtk.VBox()
		window.add(vbox)
		button = gtk.Button(_("Generate"))
		vbox.pack_start(button, False, False, 5)
		button.connect("clicked", self.generateCallBack)
		self.mGenerateButton=button
		label = gtk.Label("")
		vbox.pack_start(label, False, False, 5)
		self.mProgressLabel =label
		window.connect("done", self.doneCallBack)
		window.show_all()
		return 


            
if __name__ == '__main__':
    gettext.install("seedit-gui","/usr/share/locale")
    seeditGeneratePolicyWindow()
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
