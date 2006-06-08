#!/usr/bin/python -u
import os
import sys
import string
import re
 
from xml.dom.minidom import parse, parseString

ENFORCING=1
PERMISSIVE=0
DISABLED=-1

SEEDIT_ERROR= -1
SEEDIT_SUCCESS= 1

SEEDIT_ERROR_FILE_WRITE=-2
SEEDIT_ERROR_SEEDIT_LOAD=-3

gSELinuxConfigFile ="/etc/selinux/config"
gSPPath="/etc/seedit/policy/"
gSeedit_load= "/usr/sbin/seedit-load"

gCoreDomainList=["crond_t", "rpm_t", "gdm_t", "initrc_t", "init_t", "login_t", "unconfined_t", "rpm_script_t",  "system_crond_t", "kernel_t", "unconfined_su_t"]

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
def createDomainTemplate(program, domain , parentDomain, daemonFlag, authFlag):
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
        result = result + "include nameservice.sp;\n"
    if authFlag:
        result = result + "include authentication.sp;\n"

    result = result + "\n#Write access control here....\n\n"

    result = result + "}\n"
    return result




def saveStringToFile(str, file):

    try:
        fh = open(file, "w")
    except:
        return SEEDIT_ERROR_FILE_WRITE
    

    fh.write(str)
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


def getDeletableDomainList():
    list =getDomainList()
    result =[]

    for l in list:
        if l not in gCoreDomainList:
            result.append(l)

    result.sort()
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
