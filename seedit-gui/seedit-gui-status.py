#!/usr/bin/python


import pygtk
pygtk.require('2.0')
import gtk
import sys
import gettext
from  seedit.UILogic import *

class seeditCommon:
    """
    This class is base class for all seedit GUI Window
    """
    
    def showNotImplementedDialog(self):
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                   _("Sorry! This is not implemented yet"))
        dialog.run()
        dialog.destroy()

    def showMessageDialog(self, type, message):
        
        if type==SEEDIT_ERROR:
            dialogType=gtk.MESSAGE_ERROR
        elif type==SEEDIT_SUCCESS:
            dialogType=gtk.MESSAGE_INFO
        elif type==SEEDIT_INFO :
            dialogType=gtk.MESSAGE_INFO
            
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   dialogType, gtk.BUTTONS_OK,
                                   message)
        dialog.run()
        dialog.destroy()
    
    def notImplementedCallBack(self,w,data=None):
        self.showNotImplementedDialog()   


class loadPolicyTab(seeditCommon):
    
    #Member
    #mElement
    def configButtonCallBack(self,widget, data=None):
        print self.mType

    def radioCallBack(self,widget, data=None):
        if widget.get_active() == 1:
            self.mType = data

    def __init__(self,parent=None):
        vbox = gtk.VBox()

        radio = gtk.RadioButton(None, _("Load policy"))
        radio.connect("toggled", self.radioCallBack, "diffrelabel")
        radio.set_active(True)
        self.mType="diffrelabel"
        vbox.pack_start(radio,False,False)
        radio = gtk.RadioButton(radio, _("Initialize all lables"))
        radio.connect("toggled", self.radioCallBack, "relabel")
        vbox.pack_start(radio,False,False)
        radio = gtk.RadioButton(radio, _("Compiletest"))
        radio.connect("toggled", self.radioCallBack, "make")
        vbox.pack_start(radio,False,False)
        button = gtk.Button(_("Configure"))
        button.connect("clicked", self.configButtonCallBack)
        separator = gtk.HSeparator() 
        vbox.pack_start(separator,False,False,5)
        hbox = gtk.HBox()
        hbox.pack_start(button,False,False)
        vbox.pack_start(hbox,False,False)
    
        self.mElement = vbox
        
class domainManageTab(seeditCommon):

    #Member
    #mElement
    def configButtonCallBack(self,widget, data=None):
        print self.mType

    def radioCallBack(self,widget, data=None):
        if widget.get_active() == 1:
            self.mType = data

      
    def __init__(self,parent=None):
        vbox = gtk.VBox()

        radio = gtk.RadioButton(None, _("Add/Delete Domain/Role"))
        radio.connect("toggled", self.radioCallBack, "manageDomain")
        radio.set_active(True)
        self.mType="manageDomain"
        vbox.pack_start(radio,False,False)
        radio = gtk.RadioButton(radio, _("Configure Domain transition"))
        radio.connect("toggled", self.radioCallBack, "domaintrans")
        vbox.pack_start(radio,False,False)
        radio = gtk.RadioButton(radio, _("Manage RBAC"))
        radio.connect("toggled", self.radioCallBack, "rbac")
        vbox.pack_start(radio,False,False)
        button = gtk.Button(_("Configure"))
        button.connect("clicked", self.configButtonCallBack)
        separator = gtk.HSeparator() 
        vbox.pack_start(separator,False,False,5)
        hbox = gtk.HBox()
        hbox.pack_start(button,False,False)
        vbox.pack_start(hbox,False,False)
    
        self.mElement = vbox

class allowprivDialog:

    #mDomain: current domain
    #mParent: parent window

    def responseCallBack(self, dialog, id):
        
        if id == gtk.RESPONSE_DELETE_EVENT or id==gtk.RESPONSE_REJECT:
            dialog.destroy()

    def checkButtonCallBack(self,widget,data=None):
        print data

    def addButton(self, vbox, name, label, allowpriv):
        checked = False
        hidden = False
        if not allowpriv.has_key(name):
            pass
        else:
            allowtype = allowpriv[name]
            state = allowTypeToCbValue(allowtype,True)
            if state == HIDDEN:
                hidden = True
            elif state == CHECKED:
                checked = True
        
        button = gtk.CheckButton(label)
        button.connect("toggled", self.checkButtonCallBack, name)
        vbox.pack_start(button, False,False,0)
        if checked:
            button.set_active(True)
        if hidden:
            button.set_sensitive(False)
        button.show()

    def __init__(self,parent,domain):
        #####kernel
        #allowpriv_rule netlink klog_write klog_read  klog_adm  insmod
        #### SELinux operations
        #load_policy setenforce relabel part_relabel getsecurity setsecparam setfscreate
        #### privileges
        #net boot quotaon swapon  mount rawio ptrace chroot unlabel memlock nice resource time devcreate setattr sys_admin tty_config
        ##### Administrative huge privilege
        #search read write all
        
        self.mDomain = domain
        self.mParent= parent
        dialog = gtk.Dialog(_("Configuration for misc privileges"),
                            parent,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_APPLY, gtk.RESPONSE_ACCEPT,
                             gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        dialog.connect("response", self.responseCallBack)

        label = gtk.Label("Domain:"+self.mDomain)
        dialog.vbox.pack_start(label, False, False, 0)
        label.show()
        policy = seeditDataHolder().getPolicy()
        allowpriv = policy.getAllowPriv(domain)

        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)

        dialog.vbox.pack_start(notebook)
        vbox = gtk.VBox()
        label = gtk.Label(_("Kernel operations"))
        notebook.append_page(vbox, label)
        vbox.show()
        
        for rule in ("netlink", "klog_write", "klog_read",  "klog_adm",  "insmod"):
            self.addButton(vbox, rule, rule, allowpriv)
            
        vbox = gtk.VBox()
        label = gtk.Label(_("SELinux operations"))
        notebook.append_page(vbox, label)
        vbox.show()
        for rule in ("load_policy", "setenforce", "relabel", "part_relabel", "getsecurity","setsecparam", "setfscreate"):
            self.addButton(vbox, rule, rule, allowpriv)


        vbox = gtk.VBox()
        label = gtk.Label(_("System operations"))
        notebook.append_page(vbox, label)
        vbox.show()
        for rule in ("net", "boot", "quotaon","mount", "rawio", "ptrace", "chroot", "unlabel","memlock", "nice", "resource", "time", "devcreate" ,"setattr", "sys_admin", "tty_config"):
            self.addButton(vbox, rule, rule, allowpriv)

        vbox = gtk.VBox()
        label = gtk.Label(_("Real privileges"))
        notebook.append_page(vbox, label)
        vbox.show()
        for rule in ("search", "read", "write", "all"):
            self.addButton(vbox, rule, rule, allowpriv)
            
        notebook.show()
#        button = gtk.CheckButton("test")
#        button.connect("toggled", self.checkButtonCallBack, "check button 1")
#        dialog.vbox.pack_start(button, False,False,0)
#        button.set_active(True)
#        button.set_sensitive(False)

      
        
    #    button.show()
        
    

        dialog.run()



class accessControlTab(seeditCommon):
    #Member
    # mType: Type of configuration allowfile,allownet etc
    # mDomain: Domain: selected domain/role
    # mDomainBox,
    # mDomainList
    # mParentWindow
    
    def setDomainList(self, list):
        self.mDomainList = list
        combo = self.mDomainBox
        model = combo.get_model()
        model.clear();
        for l in list:
            combo.append_text(l)        
    
    def configButtonCallBack(self,widget, data=None):
        print self.mType
        print self.mDomain
        
        if(self.mDomain != None):
            allowprivDialog(self.mParentWindow, self.mDomain)

    def radioCallBack(self,widget, data=None):
        # print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
        if widget.get_active() == 1:
            self.mType = data

    def comboCallBack(self,widget, data=None):

        tmp = widget.get_text()
        if tmp == "":
            return        
        self.mDomain=tmp
        policy = seeditDataHolder().mPolicy

        (list, comment) =  policy.getDomainInfo(self.mDomain)
       
        text =_("Related Programs:")
        for l in list:
            text = text+l+" "
        text = text+"\n"
        text = text+ _("Comment:")+ comment
        
        self.mDetailText.set_text(text)
        
        #        print list
#        print comment

        
    def __init__(self,parent):
        vbox = gtk.VBox()
        hbox1=gtk.HBox()
        self.mParentWindow=parent
        
        #Domain selection box
        label = gtk.Label(_("Domain/Role"))
        hbox1.pack_start(label,False,False,10)
        combo = gtk.combo_box_entry_new_text()
        hbox1.pack_start(combo,False,False,10)
        
        combo.child.connect('changed', self.comboCallBack)
        combo.set_active(0)
        vbox.pack_start(hbox1,False,False)

        # Create the expander
        expander = gtk.Expander(_("Details"))
        vbox.pack_start(expander, False, False, 0)
        # The Label for the expander
        textview = gtk.TextView()
        label = gtk.Label("hoge")
        self.mDetailText = label
        expander.add(label)



        ###File
        frame = gtk.Frame(_("Related to File"))
        filevbox = gtk.VBox()
        
        radio = gtk.RadioButton(None, _("Files"))
        radio.connect("toggled", self.radioCallBack, "allowfile")
        radio.set_active(True)
        self.mType="allowfile"
        filevbox.pack_start(radio)

        radio = gtk.RadioButton(radio, _("Devices"))
        radio.connect("toggled", self.radioCallBack, "allowdev")
        filevbox.pack_start(radio)
        
        radio = gtk.RadioButton(radio, _("Files on misc filesystems"))
        radio.connect("toggled", self.radioCallBack, "allowdev")
        filevbox.pack_start(radio)
        
        frame.add(filevbox)
        vbox.pack_start(frame,False,False,10)

        ###Communication
        frame = gtk.Frame(_("Related to Communication"))
        comvbox = gtk.VBox()        

        vbox.pack_start(frame,False,False)
        radio = gtk.RadioButton(radio, _("Network"))
        radio.connect("toggled", self.radioCallBack, "allownet")
        comvbox.pack_start(radio)
        
        radio = gtk.RadioButton(radio, _("IPC(Inter Process Communication)"))
        radio.connect("toggled", self.radioCallBack, "allowcom")
        comvbox.pack_start(radio)
    
        frame.add(comvbox)

        ###Privs
        frame = gtk.Frame(_("Privileges"))
        vbox.pack_start(frame,False,False,10)
        radio = gtk.RadioButton(radio, _("Other privileges"))
        radio.connect("toggled", self.radioCallBack, "allowpriv")
        frame.add(radio)

        
        hbox = gtk.HBox()
        vbox.pack_start(hbox,False,False,10)
        button = gtk.Button(_("Configure"))
        button.connect("clicked", self.configButtonCallBack)

        hbox.pack_start(button,False,False,10)
        button = gtk.Button(_("View text configuration"))
        button.connect("clicked", self.notImplementedCallBack)

        hbox.pack_start(button,False,False,10)

        #frame = gtk.Frame(_("Description"))
        
        self.mElement = vbox
        self.mDomainBox = combo
        self.mDomainList = []

        #open file if specified from command line
        try:
            filename = sys.argv[1]
        except:
            pass
        else:
            policy = seeditDataHolder().getPolicy()
            (status, message) = policy.openPolicy(filename)
            print status

        policy = seeditDataHolder().getPolicy()
        if policy.getPolicyDoc()!=None:
            list = policy.getDomainList()
            self.setDomainList(list)
        
        
class seeditMainWindow(seeditCommon):
    ui = '''<ui>
    <menubar name="MenuBar">
      <menu action="File">
        <menuitem action="Open"/>
        <menuitem action="Save"/>
        <menuitem action="SaveAs"/>
        <menuitem action="Import"/>
        <menuitem action="Export"/>
        <menuitem action="Quit"/>
      </menu>
      <menu action="Tool">
        <menuitem action="Generate"/>
        <menuitem action="Preferences"/>
      </menu>
      <menu action="Help">
        <menuitem action="About"/>
      </menu>
      
    </menubar>
    </ui>'''
    ###Member
    #mAccessControlTab
    #mDomainManageTab
    #mLoadPolicyTab
    #mStatusLabel
    #mWindow

    def updateStatusLabel(self):
        label = self.mStatusLabel
        text =""
        policy= seeditDataHolder().mPolicy
        file =  policy.getPolicyFileName()
        modified = policy.getModified()
        text = _("Policy:%s ")%file
        if modified:
            modtext = _("Not saved")
        else:
            modtext =""
        text = text + modtext  
        label.set_text(text)

    
    def saveCallBack(self,data=None):
        policy = seeditDataHolder().mPolicy
        filename=policy.getPolicyFileName()
        (status, message) = policy.savePolicy(filename)
        self.showMessageDialog(status,message)
        self.updateStatusLabel()
        
    def saveAsCallBack(self,data=None):
        dialog = gtk.FileChooserDialog(_("Save As"),
                               None,
                               gtk.FILE_CHOOSER_ACTION_SAVE,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            policy = seeditDataHolder().mPolicy
            (status, message)=policy.savePolicy(filename)
            self.showMessageDialog(status,message)
            (status, message) = policy.openPolicy(filename)
            if message == SEEDIT_ERROR:
                self.showMessageDialog(status,message)
            self.updateStatusLabel()

        elif response == gtk.RESPONSE_CANCEL:
            pass
        dialog.destroy()
        

    def openCallBack(self,data=None):
        dialog = gtk.FileChooserDialog(_("Open policy file"),
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name(_("XML Files"))
        filter.add_pattern("*.xml")
        dialog.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name(_("All files"))
        filter.add_pattern("*")
        dialog.add_filter(filter)

       
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            policy = seeditDataHolder().mPolicy
            (status, message) = policy.openPolicy(filename)
            if status==SEEDIT_ERROR:
                self.showMessageDialog(SEEDIT_ERROR, message)
            else:
                list = policy.getDomainList()
                self.mAccessControlTab.setDomainList(list)
            self.updateStatusLabel()
                
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()
        
    def __init__(self):
        
        
        # Create the toplevel window
        window = gtk.Window()
        self.mWindow = window
        window.set_title(_("SELinux Policy Editor"))
        window.connect('destroy', lambda w: gtk.main_quit())
        window.set_resizable(False)
        vbox = gtk.VBox()
        window.add(vbox)


        # Create a UIManager instance
        uimanager = gtk.UIManager()

        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        window.add_accel_group(accelgroup)

        # Create an ActionGroup
        actiongroup = gtk.ActionGroup('seeditUIManager')
        self.actiongroup = actiongroup

        # Create actions
        actiongroup.add_actions([('Quit', gtk.STOCK_QUIT, None, None,
                                  'Quit the Program', self.quitCallBack),
                                 ('Open', gtk.STOCK_OPEN, None, None,
                                  _('Open Policy File'), self.openCallBack),
                                  ('Save', gtk.STOCK_SAVE, None, None,
                                  _('Over write and save File'), self.saveCallBack),
                                  ('SaveAs', gtk.STOCK_SAVE_AS, None, None,
                                 _('Save policy file as other name'), self.saveAsCallBack),
                                 ('Import', gtk.STOCK_CONVERT, _("_Import"), None,
                                  _('Import policy file'), self.notImplementedCallBack),
                                 ('Export', gtk.STOCK_CONVERT,_("_Export"), None,
                                  _('Export policy file'), self.notImplementedCallBack),
                                 ('File', None, _('_File')),
                                 ('Generate', gtk.STOCK_EXECUTE,_("_Generate Policy"), None,
                                  _('Generate policy from audit log'), self.notImplementedCallBack),
                                 ('Preferences', gtk.STOCK_PROPERTIES,_("_Preference"), None,
                                  _('Preference'), self.notImplementedCallBack),
                                 ('About', gtk.STOCK_HELP,_("_About"), None,
                                  _('About'), self.notImplementedCallBack),
                                 ('File', None, _('_File')),
                                 ('Help', None, _('_Help')),
                                 ('Tool', None, _('_Tool'))])

        actiongroup.get_action('Quit').set_property('short-label', '_Quit')


        # Add the actiongroup to the uimanager
        uimanager.insert_action_group(actiongroup, 0)

        # Add a UI description
        uimanager.add_ui_from_string(self.ui)

        # Create a MenuBar
        menubar = uimanager.get_widget('/MenuBar')
        vbox.pack_start(menubar, False)
     
        
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        vbox.pack_start(notebook)
        tab1 = accessControlTab(self.mWindow)
#        frame = gtk.Frame("testframe")
#        frame.set_border_width(10)
#        frame.set_size_request(100, 75)


        label = gtk.Label(_("Access Control configuration"))
        notebook.append_page(tab1.mElement, label)
        label = gtk.Label(_("Manage Domain/Role"))
        tab2 = domainManageTab()
        notebook.append_page(tab2.mElement, label)
        label = gtk.Label(_("Load policy"))
        tab3 = loadPolicyTab()
        notebook.append_page(tab3.mElement, label)
        label = gtk.Label("")
        self.mStatusLabel= label
        vbox.pack_end(label)
        window.show_all()
        self.mAccessControlTab = tab1
        self.mDomainManageTab = tab2
        self.mLoadPolicyTab = tab3
        
        return
 

    def quitCallBack(self, b):
        print 'Quitting program'
        gtk.main_quit()



if __name__ == '__main__':
    gettext.install("seedit-gui","/usr/share/locale")
    seeditMainWindow()

    gtk.main()
