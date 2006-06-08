#!/usr/bin/python
#All Rights Reserved (C) 2006, Yuichi Nakmura himainu-ynakam@miomio.jp

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import sys
import gettext
import string
sys.path.insert(0,"/usr/lib")
from  seedit.ui.GUICommon import *
from  seedit.ui.UILogic import *
from  seedit.unconfined import *

class seeditGeneratePolicyWindow(seeditCommon):
        def __init__(self):

            window = gtk.Window()
            self.mWindow = window
            window.set_title(_("Policy generater"))
            window.connect('destroy', lambda w: gtk.main_quit())
            vbox = gtk.VBox()
            window.add(vbox)

            window.show_all()
            return 


            
if __name__ == '__main__':
    gettext.install("seedit-gui","/usr/share/locale")
    seeditGeneratePolicyWindow()

    gtk.main()
