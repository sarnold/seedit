#!/usr/bin/python
import sys
import os
import getopt
import gettext
import string
import getopt
sys.path.insert(0,"/usr/lib")
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

