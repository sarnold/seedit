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

	def emit_done(self,result):
		self.mDialog.mWindow.emit("done",result)
	
	
	def __init__(self,dialog):
		threading.Thread.__init__(self)
		self.mDialog = dialog
	def run(self):
	
		gobject.idle_add(self.mDialog.mGenerateButton.set_sensitive,False)

		domdoc=readSPDLSpec(gSpecXML)
		result =[]
		input = open("test.log", 'r')
		lines = readLog(input, True)

		size = len(lines)
		i=0
		for line in lines:
			data = (i,size)
			gobject.idle_add(self.updateLabel, data)
			rule = parseLine(line)
			if(rule):
				spRuleList=genSPDL(rule,line,domdoc)
				
				list=SPDLstr(spRuleList,line)
				result.append(list)
			i = i+1				     
		data = (i,size)
		gobject.idle_add(self.updateLabel, data)
		gobject.idle_add(self.mDialog.mProgressLabel.set_text,_("Done"))
		gobject.idle_add(self.mDialog.mGenerateButton.set_sensitive,True)
		#emit "done" signal here!
		gobject.idle_add(self.emit_done,result)

	


class seeditGeneratePolicyWindow(seeditCommon):
	def generateCallBack(self,widget, data=None):

		thread = generatePolicyThread(self)
		thread.start()

        ## to avoid suggesting same rules
	def mergeSamePolicy(self, list):
		result=[]
		outputStr = dict()
		for l in list:
			(domain, log, allow) = l
			key = domain+allow

			if not outputStr.has_key(key):
				outputStr[key]=[]
			a = (domain, allow , log)
			outputStr[key].append(a)

		for key in  outputStr.keys():
			list = outputStr[key]
			log=""
			for l in list:
				domain = l[0]
				allow = l[1]
				log=log+l[2]
				
			result.append((domain,allow,log))

		return result
	'''
	When policy generation is done, it is called
	'''
        def doneCallBack(self,widget,data=None):
		treeview = self.mGeneratedPolicyTreeView
		model = treeview.get_model()
		model.clear()

		lists = data
		list =[]
		for l in lists:
			for ll in l:
				list.append(ll)
		list = self.mergeSamePolicy(list)

		for l in list:
			(domain,allow,log)=l			
			appended=(domain,allow,log)
			self.mGeneratedPolicyListStore.append(appended)
	
		return
	
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
		sw.set_size_request(300,300)
		treeview = gtk.TreeView(model)

		treeview.set_rules_hint(True)
		treeview.set_search_column(2)
		sw.add(treeview)
		self.addColumns(treeview,header)
		return (sw,treeview)

        def __init__(self):
		self.mGeneratedPolicyListStore = gtk.ListStore(
			gobject.TYPE_STRING,				
			gobject.TYPE_STRING,
			gobject.TYPE_STRING)

		
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

		header = (_("Domain"),_("Policy"),_("Log"))
		(sw,tv) = self.initTreeView(self.mGeneratedPolicyListStore,header)
		self.mGeneratedPolicyTreeView=tv

		appended=("","","")
		self.mGeneratedPolicyListStore.append(appended)

		vbox.pack_start(sw,False,False,5)
		
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
