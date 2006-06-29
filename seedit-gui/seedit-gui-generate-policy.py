#!/usr/bin/python -u
#All Rights Reserved (C) 2006, Yuichi Nakmura himainu-ynakam@miomio.jp

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import sys
import gettext
import threading
import time
import pango
sys.path.insert(0,"/usr/lib")
from  seedit.ui.GUICommon import *
from  seedit.ui.UILogic import *
from  seedit.audit2spdl import *
import seedit.audit2spdl

gRestorecon = "/sbin/restorecon"
	
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
	
		try:
			inputType = self.mDialog.mInput
			if inputType == "dmesg":
				input=os.popen("dmesg", "r")
			elif inputType == "audit.log":
				input = os.popen("/sbin/ausearch -m avc,daemon_start")
			else:				
				filename = self.mDialog.mInputFileEntry.get_text()
				
				input = open(filename,"r")

		

		except:
			gobject.idle_add(self.mDialog.mProgressLabel.set_text,_("Input error"))
			gobject.idle_add(self.mDialog.mGenerateButton.set_sensitive,True)

			gobject.idle_add(self.emit_done,result)
			return

		if self.mDialog.mReadAllLogFlag:
			lastLoad = False
		else:
			lastLoad = True
		
		lines = readLog(input, lastLoad)

		size = len(lines)
		i=0
		syscall=0
		for line in lines:

			data = (i,size)
			gobject.idle_add(self.updateLabel, data)
			rule = parseLine(line)
			newsyscall = parseSyscall(line)
			if newsyscall>0:
				syscall = newsyscall
			i = i+1
			if self.mDialog.mSkipSearchFlag:
				if rule and rule.has_key("secclass") and rule.has_key("permission") and syscall!=5:
					#syscall 5 is open, for open system call, log is not skipped
					print syscall
					if rule["secclass"]=="dir" and "search" in rule["permission"]:
						continue
			if(rule):
				spRuleList=genSPDL(rule,line,domdoc)
				
				list=SPDLstr(spRuleList,line)
				result.append(list)

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
			samelog=0
			for l in list:
				domain = l[0]
				allow = l[1]

				tmp = l[2] ##To eleminate same log
				tmp = re.sub("^type=AVC.*avc:","",tmp)
				if re.search(tmp, log):
					m = re.search("^type=AVC msg=audit\(.+\):",l[2])
					if m:
						samelog=samelog+1
				else:
					log=log+l[2]

			if samelog>0:
				samelog=_("%d samelog...") % (samelog)
			else:
				samelog=""
			log =log+samelog			
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
			log = re.sub("avc:","\n\tavc:",log)
			log = re.sub("pid=","\n\tpid=",log)
			log = re.sub("scontext=","\n\tscontext=",log)
			log = re.sub("\n$","",log)
			domain = re.sub("\.sp","",domain)
			appended=(False,domain,allow,log)
			self.mGeneratedPolicyListStore.append(appended)


		self.mNotebook.set_current_page(1)
		return

	def displayToBeAppendedPolicy(self,model):
		appendExistsFlag=False
		toBeAppendedPolicy = dict()
		appendExistsFlag = self.makeToBeAppendedPolicy(model, toBeAppendedPolicy)
		self.mTextBuffer.delete(self.mTextBuffer.get_start_iter(),self.mTextBuffer.get_end_iter())

		if appendExistsFlag:
			lines=[]
			for domain in toBeAppendedPolicy.keys():
				for rule in toBeAppendedPolicy[domain]:
					line = domain+":"+rule+"\n"
					lines.append(line)
				
			for line in lines:
				self.mTextBuffer.insert(self.mTextBuffer.get_end_iter(),line)

		toBeAppendedPolicy.clear()
		del toBeAppendedPolicy
		
	def buttonToggled(self, cell, path, model):
		iter = model.get_iter((int(path),))
		value = model.get_value(iter, 0)
		value = not value
		model.set(iter, 0, value)
		self.displayToBeAppendedPolicy(model)
	
	def allowEditedCallBack( self, cell, path, new_text, model ):
		model[path][2] = new_text
		self.displayToBeAppendedPolicy(model)
		return
	
	def addColumns(self, treeview, header):
		model = treeview.get_model()
		renderer = gtk.CellRendererToggle()
		renderer.connect('toggled', self.buttonToggled, model)
		column = gtk.TreeViewColumn(_("Save"), renderer, active=0)
		column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		column.set_fixed_width(40)
		treeview.append_column(column)


		column = gtk.TreeViewColumn(header[0], gtk.CellRendererText(),
					    text=1)
		column.set_sort_column_id(1)
		treeview.append_column(column)

		renderer=  gtk.CellRendererText()
		renderer.set_property('editable', True)
		renderer.connect( 'edited', self.allowEditedCallBack, model )
		if hasattr(pango,"ELLIPSIZE_END"):
			renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
		

		
		column = gtk.TreeViewColumn(header[1],renderer,text=2)
		column.set_sort_column_id(2)
		column.set_resizable(True)
		column.set_min_width(240)
		treeview.append_column(column)

		renderer=  gtk.CellRendererText()
#		renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
		column = gtk.TreeViewColumn(header[2], renderer,
					    text=3)
		column.set_sort_column_id(3)
#		column.set_min_width(200)

		column.set_resizable(True)

		treeview.append_column(column)
        
	def initTreeView(self,model,header):
		sw = gtk.ScrolledWindow()
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_size_request(400,300)
		treeview = gtk.TreeView(model)
		treeview.set_rules_hint(True)
		treeview.set_search_column(2)
		sw.add(treeview)
		self.addColumns(treeview,header)
		return (sw,treeview)
	
	
	def radioCallBack(self, widget, data):
		if widget.get_active() == 1:
			self.mInput= data
	def checkButtonCallBack(self,widget,data):
		if data == "allLog":
			if widget.get_active():
				self.mReadAllLogFlag=True
			else:
				self.mReadAllLogFlag=False

		elif data =="secure":
			if widget.get_active():
				seedit.audit2spdl.gHighSecurityFlag=True
			else:
				self.mSecureFlag=False
				seedit.audit2spdl.gHighSecurityFlag=False
		elif data =="skip":
			if widget.get_active():
				self.mSkipSearchFlag=True
			else:
				self.mSkipSearchFlag=False


	
	def deleteRowCallBack(self,button, treeview):
		selection = treeview.get_selection()
		model, iter = selection.get_selected()
		if iter:
			path = model.get_path(iter)[0]
			model.remove(iter)
		self.displayToBeAppendedPolicy(model)


	def removeCheckedRows(self, treeview):
		model = treeview.get_model()
		
		iter = model.get_iter_first()
		if iter:
			while iter:
				flag = model.get_value(iter,0)
				domain = model.get_value(iter,1)
				policy = model.get_value(iter,2)
				next = model.iter_next(iter)
				if flag ==  True:
					model.remove(iter)
				iter = next

	def doRestorecon(self,line):
		line  = re.sub("#restorecon","",line)
		command = gRestorecon + line
		input = os.popen(command,'r')
		print command
		input.close()

	def makeToBeAppendedPolicy(self, model,toBeAppendedPolicy):
		appendExistsFlag = False
		iter = model.get_iter_first()     
		if iter:
			while iter:
				flag = model.get_value(iter,0)
				domain = model.get_value(iter,1)
				policy = model.get_value(iter,2)
				next = model.iter_next(iter)
				if flag ==  True:
					appendExistsFlag=True
					if not toBeAppendedPolicy.has_key(domain):
						toBeAppendedPolicy[domain]=[]
					if policy[0]=='#':
						self.doRestorecon(policy)
					else:
						toBeAppendedPolicy[domain].append(policy)
				iter = next

		return appendExistsFlag
	
		
	def saveButtonCallBack(self, button, treeview):
		model = treeview.get_model()
	
		#key: domain, value: list of policy to be allowed
		toBeAppendedPolicy = dict()
		appendExistsFlag=False
		appendExistsFlag = self.makeToBeAppendedPolicy(model, toBeAppendedPolicy)	
           
		if not appendExistsFlag:
			return

		for domain in toBeAppendedPolicy.keys():
			appendPolicy(domain,  toBeAppendedPolicy[domain])

		ld=loadPolicyDialog(self)
		(s, data) = ld.do()

		if s<0:
			for domain in toBeAppendedPolicy.keys():
				restoreBackup(domain)
			self.showMessageDialog(gtk.MESSAGE_INFO, _("Syntax error was found.\n"))
			return
	        #remove saved rows
		self.removeCheckedRows(treeview)
		toBeAppendedPolicy.clear()
		
					
	def undoGlobCallBack(self,button,treeview):
		selection = treeview.get_selection()
		model, iter = selection.get_selected()
		if iter:
			value = model.get_value(iter,2)
			log = model.get_value(iter,3)
			if self.mUndoGlobDict.has_key(log):
				history = self.mUndoGlobDict[log]
				undoValue = history.pop()
				if len(history)==0:
					del self.mUndoGlobDict[log]
				model.set_value(iter,2,undoValue)

	def globCallBack(self,button,treeview):
		selection = treeview.get_selection()
		model, iter = selection.get_selected()
		if iter:
			value = model.get_value(iter,2)
			prevValue = value
			log = model.get_value(iter,3)
			if re.search("^allow[\s\t]+",value):
				path = value.split()[1]
				dirFlag=False
				if os.path.isdir(path):
					dirFlag=True

				value = re.sub("/[^/*]+\/\*\*","/**",value)
				value = re.sub("/\*[\s\t]+","/** ",value)
				if dirFlag:
					value = re.sub(path ,path+"/* ",value)

				else:	
					value = re.sub("/[^/*]*[\s\t]+","/* ",value)

				
				model.set_value(iter,2,value)
				if value!=prevValue:
					if not self.mUndoGlobDict.has_key(log):
						self.mUndoGlobDict[log]=[]
					self.mUndoGlobDict[log].append(prevValue)
					
			if re.search("^allownet[\s\t]+",value):
				m = re.search("-port[\s\t]+\d+",value)
				num = int((m.group().split())[1])
				if num >= 1024:
					value = re.sub("-port[\s\t]+\d+[\s\t]","-port 1024- ",value)
					model.set_value(iter,2,value)
					if value!=prevValue:
						if not self.mUndoGlobDict.has_key(log):
							self.mUndoGlobDict[log]=[]
						self.mUndoGlobDict[log].append(prevValue)
					
		self.displayToBeAppendedPolicy(model)

	
        def __init__(self):
		#Model for result
		self.mGeneratedPolicyListStore = gtk.ListStore(
			gobject.TYPE_BOOLEAN,
			gobject.TYPE_STRING,				
			gobject.TYPE_STRING,
			gobject.TYPE_STRING)

		#Dict for undoGlob
		#key:log, value:list of glob history
		self.mUndoGlobDict=dict()
		
		gobject.signal_new("done", gtk.Window,
				   gobject.SIGNAL_RUN_LAST,
				   gobject.TYPE_NONE,
				   (gobject.TYPE_PYOBJECT,))
		window = gtk.Window()
		self.mWindow = window
		self.mResult = []
		window.set_title(_("seedit policy generator"))
		window.connect('destroy', lambda w: gtk.main_quit())
		vboxFrame = gtk.VBox()
		window.add(vboxFrame)
		menubar = self.initMenu(window)
		vboxFrame.pack_start(menubar, False)
	
		notebook = gtk.Notebook()
		notebook.set_tab_pos(gtk.POS_TOP)
		self.mNotebook=notebook
		label = gtk.Label(_("Generation configuration"))
		vboxFrame.pack_start(notebook, False, False,5)
	
		vbox = gtk.VBox()
		frame = gtk.Frame()
		frame.add(vbox)
		notebook.append_page(frame, label)
#		vboxFrame.pack_start(frame, False, False,5)

		hbox = gtk.HBox()
		label = gtk.Label(_("Input:"))
		hbox.pack_start(label, False, False,5)
				
		radio = gtk.RadioButton(None, _("audit.log"))
		self.mInput = "audit.log"
		radio.connect("toggled", self.radioCallBack, "audit.log")
		hbox.pack_start(radio, False, False,5)
		radio = gtk.RadioButton(radio, _("dmesg"))
		radio.connect("toggled", self.radioCallBack, "dmesg")
		hbox.pack_start(radio, False, False,5)
		radio = gtk.RadioButton(radio, _("File"))
		radio.connect("toggled", self.radioCallBack, "file")
		hbox.pack_start(radio, False, False,5)
		entry = gtk.Entry()
		self.mInputFileEntry = entry
		entry.set_max_length(50)
		hbox.pack_start(entry, False, False,0)
		vbox.pack_start(hbox, False, False, 5)

		hbox = gtk.HBox()
		button = gtk.CheckButton(_("Generate more secure policy"))
		seedit.audit2spdl.gHighSecurityFlag=False
		button.connect("toggled", self.checkButtonCallBack, "secure")
		hbox.pack_start(button, False, False,0)
		vbox.pack_start(hbox, False, False, 5)
		
		hbox = gtk.HBox()
		button = gtk.CheckButton(_("Read All log"))
		self.mReadAllLogFlag=False
		button.connect("toggled", self.checkButtonCallBack, "allLog")
		hbox.pack_start(button, False, False,0)
		vbox.pack_start(hbox, False, False, 5)

		hbox = gtk.HBox()
		button = gtk.CheckButton(_("Skip search log"))
		button.set_active(True)
		self.mSkipSearchFlag=True
		button.connect("toggled", self.checkButtonCallBack, "skip")
		hbox.pack_start(button, False, False,0)
		vbox.pack_start(hbox, False, False, 5)

		hbox = gtk.HBox()
		button = gtk.Button(_("Generate"))
		hbox.pack_start(button, False, False, 5)
		button.connect("clicked", self.generateCallBack)
		self.mGenerateButton=button
		vbox.pack_start(hbox, False, False, 5)

		resultTabVBox = gtk.VBox()
		label = gtk.Label(_("Result"))
		notebook.append_page(resultTabVBox, label)

		frame=gtk.Frame(_("Result"))
		resultTabVBox.pack_start(frame, True, True,5)
		vbox = gtk.VBox()
		header = (_("Domain"),_("Policy"),_("Log"))
		(sw,tv) = self.initTreeView(self.mGeneratedPolicyListStore,header)
		self.mGeneratedPolicyTreeView=tv

		appended=(False,"","","")
		self.mGeneratedPolicyListStore.append(appended)

		

		frame.add(vbox)
		vbox.pack_start(sw,True,True,5)

		hbox=gtk.HBox()
		vbox.pack_start(hbox,False,False,5)
		button = gtk.Button(_("Glob"))
		button.connect("clicked", self.globCallBack, self.mGeneratedPolicyTreeView)
		hbox.pack_start(button, False, False, 5)
		button = gtk.Button(_("Undo Glob"))
		button.connect("clicked", self.undoGlobCallBack, self.mGeneratedPolicyTreeView)
		hbox.pack_start(button, False, False, 5)
		
		button = gtk.Button(_("Delete"))
		button.connect("clicked", self.deleteRowCallBack, self.mGeneratedPolicyTreeView)
		hbox.pack_start(button, False, False, 5)

		frame=gtk.Frame(_("Following will be saved"))
		resultTabVBox.pack_start(frame,False, False,5)
		vbox = gtk.VBox()
		frame.add(vbox)
		

		sw = gtk.ScrolledWindow()
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_size_request(400,100)
		textview = gtk.TextView()
		textview.set_editable(False)
		textbuffer = textview.get_buffer()		
		self.mTextBuffer= textbuffer
		sw.add(textview)
		vbox.pack_start(sw,False,False,5)

	
		hbox=gtk.HBox()
		button = gtk.Button(_("Save and Apply"))
		button.connect("clicked", self.saveButtonCallBack, self.mGeneratedPolicyTreeView)
		hbox.pack_start(button, False, False, 5)
		vbox.pack_start(hbox, False, False, 5)

	
		label = gtk.Label("")
		vboxFrame.pack_start(label, False, False, 5)
		self.mProgressLabel =label
		window.connect("done", self.doneCallBack)
		window.show_all()
		return 


            
if __name__ == '__main__':
	seedit.audit2spdl.gRestoreconFlag = True
	seedit.audit2spdl.gHighSecurityFlag = True
	gettext.install("seedit-gui","/usr/share/locale")
	seeditGeneratePolicyWindow()
	gtk.gdk.threads_init()
	gtk.gdk.threads_enter()
	gtk.main()
	gtk.gdk.threads_leave()
