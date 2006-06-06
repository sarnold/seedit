#!/usr/bin/python

import sys
import os
import getopt
import string
import gettext

gMakeFlags="CONFDIR=/etc/seedit/policy OUTDIR=/etc/seedit/converter/sepolicy BASEPOLICYDIR=/etc/seedit/converter/conf/base_policy MACRODIR=/etc/seedit/converter/conf/macros"

def printUsage():
    sys.stderr.write("seedit-load [-l(--load)] [-t(--test)] [-v(--verbose)] [-i (--init)]")
    sys.stderr.write(_("\t-l\tDefault behavior.Load Symplified Policy to kernel, and restore label if labeling has been changed\n"))  
    sys.stderr.write(_("\t-t\tTest of seedit-converter\n"))
    sys.stderr.write(_("\t-i\tInitialize all file labels. This takes time.\n"))
    sys.stderr.write(_("\t-v\tVerbose output\n"))
    sys.stderr.write(_("\t l,i,t option conflicts each other.\n"))
    sys.exit(1)

def doCommand(command):
    error= []
    input=os.popen(command, "r")
    line = input.readline()
    while line:
        line = string.replace(line,"\n","")
        if gVerboseFlag:
            print line
        line = input.readline()
        error.append(line)
    if input.close():
        print _("Error!:Detail is here..")
        for l in error:
            l = string.replace(l,"\n","")
            print l
        print _("#Error!! check above error message")
        return -1
    else:
        print _("seedit-load: Success")

    return 0
def doLoad():
    loadCommand = "cd /etc/seedit/converter; make diffrelabel "+gMakeFlags+" 2>&1" 
    return doCommand(loadCommand)

def doInit():
    initCommand = "cd /etc/seedit/converter; make relabel "+gMakeFlags+" 2>&1"
    print _("Initializing file labels it takes long time")
    return doCommand(initCommand)

def doTest():
    testCommand = "cd /etc/seedit/converter; make policy "+gMakeFlags+"  2>&1" 
    return doCommand(testCommand)

####Main func
if __name__ == '__main__':
    gettext.install("seedit-load","/usr/share/locale")

gVerboseFlag = False
gBehavior = "" #load,test,init

try:
    opts, args = getopt.getopt(sys.argv[1:], "tvi", ["test","verbose","init"])
except getopt.GetoptError:
    printUsage()


for opt,arg in opts:
    if opt in ("-t", "--test"):
        if(gBehavior!=""):
            printUsage()
        gBehavior="test"
    elif opt in ("-v","--verbose"):
        gVerboseFlag=True
    elif opt in ("-i","--init"):
        if(gBehavior!=""):
            printUsage()
        gBehavior="init"
    elif opt in ("-l","--load"):
        if(gBehavior!=""):
            printUsage()
        gBehavior="load"

if gBehavior=="":
    gBehavior="load"

s=0

if gBehavior == "load":
    s= doLoad()
elif gBehavior == "init":
    s= doInit()
elif gBehavior =="test":
    s= doTest()

if s<0:
    sys.exit(1)


