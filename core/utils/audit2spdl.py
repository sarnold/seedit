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
import seedit.audit2spdl

def printUsage():
    sys.stderr.write("audit2spdl [-d] [-a] [-l] [-s] [-r] [-i <inputfile> ] \n")
    sys.stderr.write("\t-d\tread input from output of /bin/dmesg\n")
    sys.stderr.write("\t-a\tread input from /var/log/audit\n")
    sys.stderr.write("\t-i\tread input from <inputfile>\n")
    sys.stderr.write("\t-l\tread input only after last load_policy and after startup of auditd\n")
    sys.stderr.write("\t-s\tGenerate more secure configuration\n")
    sys.stderr.write("\t-r\tGenerate restorecon command\n")

    sys.exit(1)


if __name__ == '__main__':
    gettext.install("audit2spdl","/usr/share/locale")


try:
    opts, args = getopt.getopt(sys.argv[1:], "i:sdvarlo:", ["input=","dmesg","verbose","audit","load_policy","output","secure"])
except getopt.GetoptError:
    printUsage()



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
        seedit.audit2spdl.gHighSecurityFlag=True
    elif opt in ("-r"):
        seedit.audit2spdl.gRestoreconFlag = True

domdoc=readSPDLSpec(gSpecXML)
lines = readLog(input, gLoadPolicyFlag)


outList=[]
i=0
size=len(lines)
for line in lines:
    
    sys.stderr.write(_("#Analyzing log. Progress:%d/%d\r") % (i,size))
    sys.stderr.flush()
    rule = parseLine(lines, i)
    if(rule):
        spRuleList=genSPDL(rule,lines,i,domdoc)        
        list=SPDLstr(spRuleList,line)
        outList.extend(list)

    i=i+1

sys.stderr.write(_("#Analyzing log. Progress:Done\n"))
printResult(outList)


#outputResult(gOutput,outputFileFlag,outList,gVerboseFlag)

