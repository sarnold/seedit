#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk
import sys
import gettext


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
        
        #if type==SEEDIT_ERROR:
        #    dialogType=gtk.MESSAGE_ERROR
        #elif type==SEEDIT_SUCCESS:
        #    dialogType=gtk.MESSAGE_INFO
        #elif type==SEEDIT_INFO :
        #    dialogType=gtk.MESSAGE_INFO

        dialogType = type
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   dialogType, gtk.BUTTONS_OK,
                                   message)
        dialog.run()
        dialog.destroy()
    
    def notImplementedCallBack(self,w,data=None):
        self.showNotImplementedDialog()
