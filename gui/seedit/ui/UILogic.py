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

import os
import sys
import string
import re
from  seedit.seedit import *

 
from xml.dom.minidom import parse, parseString

ENFORCING=1
PERMISSIVE=0
DISABLED=-1

SEEDIT_ERROR= -1
SEEDIT_SUCCESS= 1

SEEDIT_ERROR_FILE_WRITE=-2
SEEDIT_ERROR_SEEDIT_LOAD=-3

gSELinuxConfigFile ="/etc/selinux/config"

gSetsebool="/usr/sbin/setsebool"
gGetsebool="/usr/sbin/getsebool"
gRestorecon="/sbin/restorecon"
gNeedInit="/usr/share/seedit/sepolicy/need-init"
gNeedRBACInit="/usr/share/seedit/sepolicy/need-rbac-init"
gInitCommand="/usr/share/seedit/initialize/seedit-installhelper.sh"

gCoreDomainList=["crond_t", "rpm_t", "gdm_t", "initrc_t", "init_t", "login_t", "unconfined_t", "rpm_script_t",  "system_crond_t", "kernel_t", "unconfined_su_t"]
gRpmPath="/bin/rpm"
gSkipPatternString = ["^/usr/share/doc/.*", "^/usr/share/man/.*","^/etc/rc.d/.*","^/etc/logrotate.d/.*"]

def getMode():
    try:
        fh = open("/selinux/enforce", 'r')
    except:
        return DISABLED
    mode = fh.readline()
    fh.close()
    
    if mode == "0":
        return PERMISSIVE
    elif mode == "1":
        return ENFORCING



def setMode(mode):
    if mode == getMode():
        return SEEDIT_SUCCESS
    
    try:
        fh = open("/selinux/enforce", 'w')
        if mode == PERMISSIVE:
            fh.write("0")
        elif mode == ENFORCING:
            fh.write("1")
        else:
            SEEDIT_ERROR
    except:
        return SEEDIT_ERROR

    fh.close()
    return SEEDIT_SUCCESS


def setBootMode(mode):
    if mode == getBootMode():
        return SEEDIT_SUCCESS
    

    tmpfh = os.tmpfile()
    try:
        fh = open(gSELinuxConfigFile, 'r')
        lines = fh.readlines()
        fh.close()
    except:
        tmpfh.close()
        return SEEDIT_ERROR

    pat = re.compile("^[\s\t]*SELINUX[\s\t]*=")
    for line in lines:
        m = pat.search(line)
        if m:
            if mode == ENFORCING:
                tmpfh.write("SELINUX=enforcing\n")
            elif mode == PERMISSIVE:
                tmpfh.write("SELINUX=permissive\n")
            else:
                tmpfh.write("SELINUX=disabled\n")
        else:
            tmpfh.write(line)

    tmpfh.seek(0)
    lines = tmpfh.readlines()
    try:
        fh = open(gSELinuxConfigFile, 'w')
    except:
        tmpfh.close()
        return SEEDIT_ERROR
    
    for line in lines:
        fh.write(line)
    fh.close()

    return SEEDIT_SUCCESS


def getRBAC():
    if os.path.exists(gSPPath+"/sysadm_r.sp"):
        return True
    return False

def setRBAC(mode):
    currentMode = getRBAC()

    if mode==currentMode:
        return SEEDIT_SUCCESS

    

    return SEEDIT_ERROR

    
    
def getBootMode():
    try:
        fh = open(gSELinuxConfigFile, 'r')
    except:
        return DISABLED

    lines = fh.readlines()
    fh.close()
    pat = re.compile("^[\s\t]*SELINUX[\s\t]*=")
    for line in lines:
        m = pat.search(line)
        if m:
            list = string.split(line,"=")
            mode = list.pop()
            mode = string.strip(mode)
            mode = string.lower(mode)
            if mode == "permissive":
                return PERMISSIVE
            elif mode == "enforcing":
                return ENFORCING
            else:
                return DISABLED
    return DISABLED





def seeditInstalled():
    try:
        fh = open(gSELinuxConfigFile, 'r')
    except:
        return DISABLED

    lines = fh.readlines()
    fh.close()
    pat = re.compile("^[\s\t]*SELINUXTYPE[\s\t]*=")
    for line in lines:
        m = pat.search(line)
        if m:
            list = string.split(line,"=")
            mode = list.pop()
            mode = string.strip(mode)
            mode = string.lower(mode)
            if mode == "seedit":
                return True
            else:
                return False

    return False


'''
Error : return None
'''
def createDomainTemplate(program, domain , parentDomain, daemonFlag, authFlag,desktopFlag):
    result=""
    result = "{\n"

    if not re.search("\w_t$", domain):
        return None

    result = result + "domain "+domain +";\n"
    
    if program:
        result = result +"program "+program+";\n"

    if re.search("\w_t$",parentDomain):
        result = result +"domain_trans "+parentDomain+" "+program+";\n"

    result = result + "include common-relaxed.sp;\n"

    if daemonFlag:
        result = result + "include daemon.sp;\n"
        result = result + "include logfile.sp;\n"
        result = result + "include nameservice.sp;\n"
    if authFlag:
        result = result + "include authentication.sp;\n"
    if desktopFlag:
        result = result +"include xapps.sp;\n"
        result = result +"include tmpfile.sp;\n"
        result = result +"include nameservice.sp;\n"


    result = result + "\n#Write access control here....\n\n"

    result = result + "}\n"
    return result



def fileString(filename):
    string = ""
    try:
        fh = open(filename, "r")
    except:
        print "File open error:%s" % (filename)
        return ""

    lines = fh.readlines()

    for line in lines:
        string = string + line

    return string
    

def saveStringToFile(str, file):

    try:
        fh = open(file, "w")
    except:
        return SEEDIT_ERROR_FILE_WRITE
    

    fh.write(str)
    fh.close
    return SEEDIT_SUCCESS

def saveListToFile(list, file):

    try:
        fh = open(file, "w")
    except:
        return SEEDIT_ERROR_FILE_WRITE
    
    for l in list:
        fh.write(l)
    
    fh.close
    return SEEDIT_SUCCESS


#do seedit-load
def loadPolicy():
    command = gSeedit_load+" -v"
    input=os.popen(command+ ' 2>&1', "r",0)
    while 1:
       line = input.readline()
       if not line:
           break
       else:
           sys.stdout.write(line)
           sys.stdout.flush()
       
    if input.close():
        return SEEDIT_ERROR_SEEDIT_LOAD
    
    return SEEDIT_SUCCESS
    

def createDomain(data, file):

    #Save to file
    r = saveStringToFile(data,file)
    if r<0:
        return r


    #seedit-load,
    #if err, delete and seedit-load again
    r = loadPolicy()
    if r<0:
        os.unlink(file)
        loadPolicy()
        return r
    return SEEDIT_SUCCESS


def getIncludeList():
    result = []
    path = gSPPath+"/include"
    list = os.listdir(path)
    pat = re.compile("\.sp$")
    
    for l in list:
        m = pat.search(l)
        if m:
            include = "include/"+l
            result.append(include)

    return result

def getDomainList():
    result =[]
    list = os.listdir(gSPPath)

    pat = re.compile("\.sp$")
    
    for l in list:
        if l == "all.sp":
            continue
        m = pat.search(l)
        if m:
            domain = re.sub("\.sp$","",l)            
            result.append(domain)

    return result

def getExtraDomainList():
    result =[]
    list = os.listdir(gSPPath+"/extras/")

    pat = re.compile("\.sp$")
    
    for l in list:
        if l == "all.sp":
            continue
        m = pat.search(l)
        if m:
            domain = re.sub("\.sp$","",l)            
            result.append(domain)

    return result




def getDeletableDomainList():
    list =getDomainList()
    disabled=getDisableTransDomain()
    result =[]

    for l in list:
        if l not in gCoreDomainList:
            if l not in disabled:
                result.append(l)

    result.sort()
    return result


def getDomainFileName(domain):
    if re.search("\.sp$",domain):
        #for include/
        filename = gSPPath + domain
    else:
        filename = gSPPath + domain +".sp"
    return filename

def getExtraDomainFileName(domain):
    filename = gSPPath + "/extras/"+domain +".sp"
    return filename


def getEditableDomainList():
    list =getDomainList()
    result =[]
    for l in list:
        if l not in "all":
            result.append(l)

    result.sort()

    list = getIncludeList()
    list.sort()
    for l in list:
        result.append(l)
    
    return result


'''
Returns (<list of related programs>, <Flag whether domain is confined, if unconfined False>)
error:None
'''
def getDomainProperty(domain):
    programList =[]
    confinedFlag =  True

    file = gSPPath+domain+".sp"
    try:
        input = open(file,'r')
    except:
        return None
    
    lines = input.readlines()

    input.close()
    for line in lines:
        m = re.search("^\s*allowpriv\s+all\s*;",line)
        if m:
            confinedFlag =False
            continue
        m = re.search("^\s*program\s+",line)
        if m:
            line = re.sub(";","",line)
            line = re.sub("^\s*program\s+","",line)
            line = re.sub("\n","",line)
            programList.append(line)
            continue

        m = re.search("^\s*domain_trans\s+",line)
        if m:
            line = re.sub("^\s*domain_trans\s+","",line)
            line = re.sub("\n","",line)
            s = line.split()
            programList.append(s[0])
            continue        
    
    return (programList, confinedFlag)

def setDisableTransBoolean(domain,value):
    prefix = re.sub("_t$", "" , domain)
    bool = prefix + "_disable_trans"
    if value=="on":
        value = "1"
    elif value=="off":
        value ="0"
    
    command = gSetsebool +" -P "+bool +" "+value
    print command
    input=os.popen(command, "r")
    line = input.readlines()
    if input.close():
        return SEEDIT_ERROR

    return SEEDIT_SUCCESS

def deleteDomain(domain, temporalFlag):

    if temporalFlag:
        return setDisableTransBoolean(domain,"on")

    filename = gSPPath + domain +".sp"
    newname = gSPPath +"/extras/" +domain+".sp"
    try:
        os.rename(filename, newname)
        #os.unlink(filename)
    except:
        return SEEDIT_ERROR
    return SEEDIT_SUCCESS
    
'''

Return list of domains whose _disable_trans is on
Error:None

'''
def getDisableTransDomain():
    result = []
    command = gGetsebool +" -a"
    input=os.popen(command, "r")
    lines = input.readlines()
    if input.close():
        return None

    for line in lines:
        m = re.search("_disable_trans", line)
        if m:
            m = re.search("-->\s*(on|active)",line)
            if m:
                l = line.split()
                bool = l[0]
                prefix = re.sub("_disable_trans$","",bool)
                domain = prefix+"_t"
                result.append(domain)
            
    
    return result


def restoreBackup(domain):
    filename = gSPPath +domain+".sp"
    backupfile = gSPPath +domain+".sp.backup"
    os.rename(backupfile, filename)    

'''
Append allows in  policyList to domain
Append allows before }
'''
def appendPolicy(domain, policyList):

    filename = gSPPath +domain+".sp"
    backupfile = gSPPath +domain+".sp.backup"
    
    
    try :
        fp = open(filename,'r+')
    except:
        print "File open error %s" %(filename)
        return SEEDIT_ERROR
    try:
        bfp = open(backupfile,'w')
    except:
        print "File open error %s" %(backupfile)
        return SEEDIT_ERROR

    lines = fp.readlines()
    for line in lines:
        bfp.write(line)
    bfp.close()
    fp.seek(0)
    
    line = fp.readline()
    while not re.search("^[^#]*}",line):
        pos = fp.tell()
        line = fp.readline()
        lastLine = line
        if not line:
            break

    
    if not lastLine:
        fp.close()
        return
    fp.seek(pos)
    fp.write("#Add by seedit-generator\n")
    for policy in policyList:
        fp.write(policy)
        fp.write('\n')
    
    fp.write(lastLine)
    fp.close()

    return SEEDIT_SUCCESS


'''
make SPDL expression
file, filename
dirType: itself,direct,all
permission: dict, key:permission, value:boolean
'''
def allowFileStr(file, dirType, permission):
    file =file.rstrip()
    file =file.rstrip('/')

    if file=="":
        return ""
    

    if dirType=="itself":
        pass
    elif dirType=="direct":
        file = file+"/*"
    elif dirType =="all":
        file = file+"/**"

    keys = permission.keys()
    permStr=""
    for key in keys:
        if permission[key]:
            permStr=permStr+key+','

    permStr = permStr.rstrip(',')
    if permStr=="":
        return ""
    

    str = "allow "+file+" "+permStr+";\n"
    return str

def checkPortText(portText):
    portText=portText.rstrip()
    m = re.search("^\d+$",portText)
    if m:
        return True
    m = re.search("^(\d+,)+\d+$",portText)
    if m:
        return True
    return False

'''
Logic to make allownet from add policy dialog
'''
def allowNetStr(protocol, portType, portText, serverFlag, clientFlag):
    if protocol=="raw":
        return "allownet -protocol raw use;\n"

    port =""
    if portType == "specific":
        if checkPortText(portText):
            port =  portText
    elif portType == "wellknown":
        port ="-1023"
    elif portType == "unpriv":
        port ="1024-"
    elif portType =="all":
        port ="*"
    if port=="":
        return ""
    
    perm=""
    if serverFlag:
        perm ="server"
    if clientFlag:
        if perm=="":
            perm = "client"
        perm = perm+",client"
    
    if perm=="":
        return ""
    
    str = "allownet -protocol %s -port %s %s;\n" % ( protocol, port, perm)
    
    return str

def createRoleTemplate(user, role, remoteLoginFlag,dacSkipFlag):
    result=""
    result = "{\n"

    if not re.search("\w_r$", role):
        return None

    result = result + "role "+role +";\n"
    
    if user:
        result = result +"user "+user+";\n"

    if remoteLoginFlag:
        result = result +"include remote_login.sp;\n"
    
    result = result + "include user_common.sp;\n"
    result = result + "include common-relaxed.sp;\n"

    if dacSkipFlag:
        result = result +"allowpriv cap_dac_override;\n"
        result = result +"allowpriv cap_dac_read_search;\n"

    result = result +"allow ~/** r,w,x,s;\n"


    result = result + "\n#Write access control here....\n\n"

    result = result + "}\n"
    return result



def getRelatedFileList(path,skipPatternReg):
    result = []
    command = gRpmPath+" -ql `"+gRpmPath+" -qf "+path+"`"
    try:
        input=os.popen(command, "r")
    except:
        return None

    lines = input.readlines()
    for r in skipPatternReg:
        newLines=[]
        for l in lines:
            m = r.search(l)
            if m:
                pass
            else:
                newLines.append(l)
        lines = newLines
        
    for l in lines:
       l = l.replace("\n","")
       result.append(l)

    return result

def removeChildDir(list):
    result = []
    list.sort()
    r = re.compile(list[0])
    result.append(list[0])
    for l in list:
        m = r.search(l)
        if m:
            pass
        else:
            result.append(l)
            r = re.compile("^"+l)
    return result


#Guess files related to program(path is |path|) by rpm command
def guessRelatedFile(path):
    result = []
    skipPatternReg = []
    for s in gSkipPatternString:
        r = re.compile(s)
        skipPatternReg.append(r)

    list = getRelatedFileList(path,skipPatternReg)
    if list == None:
        return None
    list = removeChildDir(list)
    for l in list:
        if os.path.isdir(l):
            result.append(l+"/**")
        else:
            result.append(l)
    return result


def guessRelatedFileAllow(path):
    result = ""
    list = guessRelatedFile(path)
    if list:
        for l in list:
            s = "allow "+l+" r,s;\n"
            result = result +s
    
    return result
