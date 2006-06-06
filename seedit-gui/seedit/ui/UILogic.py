#!/usr/bin/python
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

gSELinuxConfigFile ="/etc/selinux/config"
gSPPath="/etc/seedit/policy/"

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
