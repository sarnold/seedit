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
import re
import getopt


def getUnconfinedDomains(filename):
    unconfinedDomains = []
    try:
        fh = open(filename)
    except:
        sys.stderr.write(_("Input file open error:%s") % filename)
        sys.exit(1)

    l = fh.readline()
    while l:
        l = string.replace(l,"\n","")
        unconfinedDomains.append(l)
        l = fh.readline()
    return unconfinedDomains

def makeDomainStr(line,unconfinedDomainsList):
    line = string.replace(line,"\n","")
    pat=re.compile("\S+:\S+:\S+$")
    m = pat.search(line)
    if m:
        context = m.group()
        a = string.split(context,":")
        domain = a[2]
    else:
        return ""

    if domain in unconfinedDomainsList:
        str = _("Unconfined(%s)") % domain
    else:
        str = _("Confined by %s") % domain

    return str
    
def getWorkingProcessList(unconfinedDomainsList):
    list =[]
    input=os.popen("/bin/ps -e -o pid -o comm=Command -o label", "r")
    lines = input.readlines()
    for line in lines:
       domainStr=makeDomainStr(line,unconfinedDomainsList)
       a = string.split(line)
       pid = a[0]
       comm = a[1]
       if domainStr:
           list.append((pid,comm,domainStr))
    return list

def showWorkingProcess(list):
    print "PID\tComm\tDomain\n"
    for e in list:
        print "%s\t%s\t%s" % e

def searchDomainByPid(pid):
    #/proc/<pid>/attr/current
    filename = "/proc/"+pid+"/attr/current"
    try:
        fh = open(filename)
    except:
        sys.stderr.write(_("Pid file open error:%s") % filename)
        sys.exit(1)

    lines = fh.readlines()
    context = lines[0]
    a = string.split(context,":")
    domain = a[2]
    #remove special character at the end of attr/current
    m = re.compile("\w+").search(domain)
    if m:
        return m.group()
    return ""

def showCurrentMode():
    mode =""
    input=os.popen(" /usr/sbin/getenforce", "r")
    lines = input.readlines()
    input.close()
    for line in lines:
        mode = line + mode
    print _("Current SELinux mode: %s") % mode

def getProgNameByPid(pid):
    prog = os.readlink("/proc/"+pid+"/exe")
    return prog


def getPortStr(line):
    list = string.split(line)
    proto = list[0]
    local = list[3]
    list = string.split(local,":")
    port = list.pop()
    return proto+"/"+port


def getNetworkProcessList(unconfinedDomainsList):
    list =[]
    input=os.popen("/bin/netstat -nlp", "r")
    lines = input.readlines()
    for line in lines:
        line = string.replace(line,"\n","")
        pat=re.compile("^(tcp|udp)\s+")
        m = pat.search(line)
        if m:
            pat = re.compile("\d+/")
            m = pat.search(line)
            if m:
                pid = m.group()
                pid = string.replace(pid,"/","")
                domain = searchDomainByPid(pid)
                prog = getProgNameByPid(pid)
                if domain in unconfinedDomainsList:
                    str = _("Unconfined(%s)") % domain
                else:
                    str = _("Confined by %s") % domain
                line = line + str
                port = getPortStr(line)
                list.append( (port,prog, str))
    return list

    
def showNetworkProcess(list):
    for e in list:
        print "%s\t%s\t%s" % e
