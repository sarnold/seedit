#!/usr/bin/python -u

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
import re
import getopt
import string
import gettext
from seedit.seedit import *


gMakeFlags="CONFDIR=/etc/seedit/policy OUTDIR=/usr/share/seedit/sepolicy BASEPOLICYDIR=/usr/share/seedit/base_policy MACRODIR=/usr/share/seedit/macros"
gAuditCtl="/sbin/auditctl"
gStartStr ="# Added by seedit"
gEndStr = "# End of seedit"

def getConfinedDomains(filename):
    confinedDomains = []
    try:
        fh = open(filename)
    except:
        sys.stderr.write(_("Input file open error:%s") % filename)
        return None

    l = fh.readline()
    while l:
        l = string.replace(l,"\n","")
        confinedDomains.append(l)
        l = fh.readline()
    return confinedDomains

def getAuditRulesFileName():
    filename="/etc/audit.rules"
        
    try:
        fh = open(filename)
    except:
        filename = "/etc/audit/audit.rules"
        try:
            fh = open(filename)
        except:
            #audit is not installed
            return ""
    fh.close()
    return filename


        
def removeAuditChdirFromAuditRulesFile():
    filename=getAuditRulesFileName()
    if filename=="":
        return
    try:
        fh = open(filename)
    except:
        sys.exit(1)

    lines=fh.readlines()
    lineBuf=[]
    sreg = re.compile(gStartStr)
    flag = True
    for line in lines:
        m = sreg.search(line)
        if m:
            flag = False
	if flag:
        	lineBuf.append(line)

    fh.close()

    try:
        fh = open(filename,"w")
    except:
        print "File open error"+filename
        sys.exit(1)

    for line in lineBuf:
        fh.write(line)
    fh.close()


def forkExec(command,verbose=False):
    if verbose:
        print command
    pid = os.fork()
    if pid==0:
        os.system(command)
        sys.exit(0)
    os.wait()
     

def removeAuditChdir():
     removeAuditChdirFromAuditRulesFile()
     confinedDomains=getConfinedDomains("/usr/share/seedit/sepolicy/confined_domains")
     command = gAuditCtl+" -d exit,always -S chdir"+"  >/dev/null 2>&1 "
     
     forkExec(command,gVerboseFlag)
     
     
     if confinedDomains==None:
         return
          
     for domain in confinedDomains:
         command = gAuditCtl+" -d exit,always -S chdir -F obj_type="+domain+" >/dev/null 2>&1 "
         if gAuditChdirFlag==True:
             forkExec(command,gVerboseFlag)
     return

#audit chdir syscall to obtain full path when program chroots
#audit only for confined domains
def doAuditChdir():
    confinedDomains=getConfinedDomains("/usr/share/seedit/sepolicy/confined_domains")
    if confinedDomains==None:
        return

    command = gAuditCtl+" -a exit,always -S chroot"
    forkExec(command, gVerboseFlag)
    for domain in confinedDomains:
        command = gAuditCtl+" -a exit,always -S chdir -F obj_type="+domain
        command = command +" >/dev/null 2>&1 "
        forkExec(command,gVerboseFlag)

    filename = getAuditRulesFileName()
    try:
        fh = open(filename)
    except:
        print "File open error"+filename
        sys.exit(1)

    lines = fh.readlines()
    lineBuf=[]
    for line in lines:
        lineBuf.append(line)
    lineBuf.append(gStartStr+"\n")
    lineBuf.append("-a exit,always -S chroot\n") 
    for domain in confinedDomains:
        s = "-a exit,always -S chdir -F obj_type="+domain+"\n"
        lineBuf.append(s)
    lineBuf.append(gEndStr+"\n")

    try:
        fh = open(filename,"w")
    except:
        print "File open error"+filename
        sys.exit(1)

    for line in lineBuf:
        fh.write(line)
    fh.close()

#logs all chdir 
def doAuditChdirAll():
    
    command = gAuditCtl+" -a exit,always -S chdir >/dev/null 2>&1"
    forkExec(command,gVerboseFlag)

    filename = getAuditRulesFileName()
    try:
        fh = open(filename)
    except:
        print "File open error"+filename
        sys.exit(1)

    lines = fh.readlines()
    lineBuf=[]
    for line in lines:
        lineBuf.append(line)
    

    s = "-a exit,always -S chdir\n"
    lineBuf.append(s)
    try:
        fh = open(filename,"w")
    except:
        print "File open error"+filename
        sys.exit(1)

    for line in lineBuf:
        fh.write(line)
    fh.close()



def printUsage():
    sys.stderr.write("seedit-load [-l(--load)] [-t(--test)] [-v(--verbose)] [-i (--init)]  [-d(--deploy)]")
    sys.stderr.write(_("\t-l\tDefault behavior.Load Symplified Policy to kernel, and restore label if labeling has been changed\n"))  
    sys.stderr.write(_("\t-t\tTest of seedit-converter\n"))
    sys.stderr.write(_("\t-i\tInitialize all file labels. This takes time.\n"))
    sys.stderr.write(_("\t-v\tVerbose output\n"))
    sys.stderr.write(_("\t-e\tVerbose output, to stderr\n"))
    sys.stderr.write(_("\t-n\tDo not audit chdir logs(Effective only after FC5)\n"))
    sys.stderr.write(_("\t-a\tAudit all chdir logs(Will generate lots of logs\n"))
    sys.stderr.write(_("\t-d\tDeploy poilcy to /etc/selinux/seedit. When cross install, it is installed in ./policy_root.\n"))
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
        if gVerboseStderrFlag:
            sys.stderr.write(line)
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
    if gCross:
        loadCommand = "./seedit-cross.sh build 2>&1" 
    else:
        loadCommand = "cd /usr/share/seedit; make diffrelabel "+gMakeFlags+" 2>&1" 
    return doCommand(loadCommand)

def doDeploy():
    if gCross:
        loadCommand = "./seedit-cross.sh build 2>&1; ./seedit-cross.sh diff; ./seedit-cross.sh install 2>&1" 

    else:
        loadCommand = "cd /usr/share/seedit; make install "+gMakeFlags+" 2>&1" 

    return doCommand(loadCommand)

def doInit():
    if gCross:
        return

    initCommand = "cd /usr/share/seedit; make relabel "+gMakeFlags+" 2>&1"
    print _("Initializing file labels it takes long time")
    return doCommand(initCommand)

def doTest():
    if gCross:
        testCommand = "./seedit-cross.sh build  2>&1" 
    else:
        testCommand = "cd /usr/share/seedit; make policy "+gMakeFlags+"  2>&1" 
    return doCommand(testCommand)

####Main func
if __name__ == '__main__':
    gettext.install("seedit-load","/usr/share/locale")

gVerboseStderrFlag=False
gVerboseFlag = False
gBehavior = "" #load,test,init
gAuditChdirFlag = True  #-n option
gAuditChdirAllFlag = False #-a option

# Check audit_chdir field in /etc/seedit/seedit-load.conf
if gCross == False:
    try:
        input = open(gSeeditLoadConf, 'r')
    
        lines = input.readlines()
        for line in lines:
            list = string.split(line)
            try:
                if list[0] == "audit_chdir":
                    if list[1] == "n":
                        gAuditChdirFlag = False
            except:
                pass
        input.close()
    except:
        print "File Open Error:"+gSeeditLoadConf+" Skipped.\n"

    print "Audit chdir:"
    print gAuditChdirFlag

try:
    opts, args = getopt.getopt(sys.argv[1:], "atnveird", ["audit","test","noaudit","verbose","init","remove-audit","deploy"])
except getopt.GetoptError:
    printUsage()


for opt,arg in opts:
    if opt in ("-t", "--test"):
        if(gBehavior!=""):
            printUsage()
        gBehavior="test"
    elif opt in ("-v","--verbose"):
        gVerboseFlag=True
    elif opt in ("-n","--noaudit"):
        gAuditChdirFlag=False
    elif opt in ("-a","--audit"):
        gAuditChdirAllFlag=True
        gAuditChdirFlag=False
    elif opt in ("-e"):
        gVerboseStderrFlag=True
    elif opt in ("-i","--init"):
        if(gBehavior!=""):
            printUsage()
        gBehavior="init"
    elif opt in ("-l","--load"):
        if(gBehavior!=""):
            printUsage()
        gBehavior="load"
    elif opt in ("-d", "--deploy"):
        gBehavior="deploy"
    elif opt in ("-r","--remove-audit"):
        if(gBehavior!=""):
            printUsage()
        gBehavior="remove-audit"

if gBehavior=="":
    gBehavior="load"

if os.path.exists("/usr/share/seedit/sepolicy/seedit-rbac-init"):
    print "Error: You have to initialize RBAC."
    print "Type /usr/share/seedit/script/seedit-installhelper.sh upgrade"
    sys.exit(1)

if gBehavior == "remove-audit":
    removeAuditChdir()
    sys.exit(0)

#Handles logging for chdir syscall
if gBehavior not in  ("test","deploy") and gCross == False:
    removeAuditChdir()
    if gAuditChdirFlag==True:
        doAuditChdir()
    if gAuditChdirAllFlag==True:
        doAuditChdirAll()

s=0

if gBehavior == "load":
    s= doLoad()
elif gBehavior == "init":
    s= doInit()
elif gBehavior =="test":
    s= doTest()
elif gBehavior =="deploy":
    s= doDeploy()
    removeAuditChdir()
    if gAuditChdirFlag == True and gCross == False:
	doAuditChdir()
    if gAuditChdirAllFlag == True and gCross == False:
	doAuditChdirAll()

if s<0:
    sys.exit(1)


