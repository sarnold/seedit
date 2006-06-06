#!/usr/bin/python
# Author: Yuichi Nakamura <ynakam@gwu.edu>
# Copyright (c) 2006 Yuichi Nakamura
# License: GPL

"""
This generates simplified policy from log like audit2allow

"""

from xml.dom.minidom import parse, parseString
import os
import sys
import string
import re
import getopt
import gettext
sys.path.insert(0,"/usr/lib")
from seedit.audit2spdl import *


def printUsage():
    sys.stderr.write("audit2spdl [-d] [-a] [-l] [-s] [-i <inputfile> ] \n")
    sys.stderr.write("\t-d\tread input from output of /bin/dmesg\n")
    sys.stderr.write("\t-a\tread input from /var/log/audit\n")
    sys.stderr.write("\t-i\tread input from <inputfile>\n")
    sys.stderr.write("\t-l\tread input only after last load_policy and after startup of auditd\n")
    sys.stderr.write("\t-s\tGenerate more secure configuration\n")

    sys.exit(1)


if __name__ == '__main__':
    gettext.install("audit2spdl","/usr/share/locale")


try:
    opts, args = getopt.getopt(sys.argv[1:], "i:sdvalo:", ["input=","dmesg","verbose","audit","load_policy","output","secure"])
except getopt.GetoptError:
    printUsage()

domdoc=readSPDLSpec(gSpecXML)

input = getInput(opts)

outputFileFlag=False
for opt,arg in opts:
    if opt in ("-l", "--load_policy"):
        gLoadPolicyFlag=True
    elif opt in ("-v","--verbose"):
        gVerboseFlag=True
    elif opt in ("-o","--output"):
        outputFileFlag=True
        if arg!="":
            gOutput=arg
    elif opt in ("-s","--secure"):
        gHighSecurityFlag=True

lines=input.readlines()
lineBuf=[]

if gLoadPolicyFlag:
    reg = re.compile("avc:.*granted.*{.*load_policy.*}")
    reg2= re.compile("type=DAEMON_START.*auditd.*start")
    
    for line in lines:
        lineBuf.append(line)
        m = reg.search(line)
        m2 = reg2.search(line)
        if m or m2:
            del lineBuf
            lineBuf=[]
            
    del lines
    lines=lineBuf

outList=[]
i=0
size=len(lines)
for line in lines:

    sys.stderr.write(_("#Analyzing log. Progress:%d/%d\r") % (i,size))
    sys.stderr.flush()
    rule = parseLine(line)
    if(rule):
        spRuleList=genSPDL(rule,line,domdoc)
        
        list=SPDLstr(spRuleList,line)
        outList.extend(list)

    i=i+1

sys.stderr.write(_("#Analyzing log. Progress:Done\n"))
printResult(outList)


#outputResult(gOutput,outputFileFlag,outList,gVerboseFlag)

