#!/usr/bin/python

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

import sys
import os
import getopt
import gettext
import string
import getopt
from  seedit.unconfined import *

def printUsage():
    sys.stderr.write(_("seedit-unconfined [-e(--exe)] [-n(--net)]\n"))
    sys.stderr.write(_("\t-e\tShow domain of running programs\n"))  
    sys.stderr.write(_("\t-n\tShow domain of network accepting programs\n"))
    sys.exit(1)


###main###
if __name__ == '__main__':
    gettext.install("seedit-unconfined","/usr/share/locale")

gUnconfinedDomains=[] #List of unconfined domains

gUnconfinedDomains = getUnconfinedDomains("/etc/selinux/seedit/policy/unconfined_domains")
gBehavior=""

try:
    opts, args = getopt.getopt(sys.argv[1:], "en", ["exe","net"])
except getopt.GetoptError:
    printUsage()

for opt,arg in opts:
    if opt in ("-e", "--exe"):
        if(gBehavior!=""):
            printUsage()
        gBehavior="exe"
    elif opt in ("-n","--net"):
        if(gBehavior!=""):
            printUsage()
        gBehavior="net"


if gBehavior=="":
    printUsage()

showCurrentMode()

if gBehavior=="exe":
    showWorkingProcess(getWorkingProcessList(gUnconfinedDomains))
if gBehavior=="net":
    showNetworkProcess(getNetworkProcessList(gUnconfinedDomains))

