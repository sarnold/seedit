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
	def __init__(self,dialog):
		threading.Thread.__init__(self)
		self.mDialog = dialog
	def run(self):
		domdoc=readSPDLSpec(gSpecXML)
		print "hoge"
		result =[]
		self.mDialog.mProgressLabel.set_text("Progress:")
		input = open("test.log", 'r')
		lines = readLog(input, True)

		size = len(lines)
		i=0
		for line in lines:
		#	self.mDialog.mProgressLabel.set_text(_("Progress:%d/%d") % (i,size))
			
			print i
			rule = parseLine(line)
			if(rule):
				spRuleList=genSPDL(rule,line,domdoc)
				
				list=SPDLstr(spRuleList,line)
				print list
			i = i+1				     



		self.mDialog.mResult=result
		self.mDialog.mProgressLabel.set_text(_("Progress:%d/%d") % (size,size))
		self.mDialog.mProgressLabel.show()


		
class generateDialog(gtk.Dialog):
	def showCallback(self, data=None):
		thread = generatePolicyThread(self)
		thread.start()
	
	
	def generate(self):
		pass
		r = self.run()
		self.destroy()
		self.mParent.present()
		self.mParent.raise_()
		self.mParent.show_all()
		self.mParent.map()
		
	
	def __init__(self,parent):
		self.mResult = [] #To store generated policy
		self.mParent = parent
		gtk.Dialog.__init__(self,_("load policy"),parent, gtk.DIALOG_MODAL,(gtk.STOCK_OK, gtk.RESPONSE_CANCEL))
		label= gtk.Label(_("Generating Policy... It may take time."))
		self.vbox.pack_start(label, False, False,0)
		self.mProgressLabel = label

		self.connect("show", self.showCallback) #on show, generation thread run
		self.show_all()


class seeditGeneratePolicyWindow(seeditCommon):
	def generateCallBack(self,widget, data=None):
		g = generateDialog(self.mWindow)
		g.generate()
		print g.mResult
	
        def __init__(self):
		window = gtk.Window()
		self.mWindow = window
		window.set_title(_("Policy generater"))
		window.connect('destroy', lambda w: gtk.main_quit())
		vbox = gtk.VBox()
		window.add(vbox)
		button = gtk.Button(_("Generate"))
		vbox.pack_start(button, False, False, 5)
		button.connect("clicked", self.generateCallBack)
		window.show_all()
		return 


            
if __name__ == '__main__':
    gettext.install("seedit-gui","/usr/share/locale")
    seeditGeneratePolicyWindow()
    gtk.gdk.threads_init()

    gtk.main()
