#! /usr/bin/python
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
Functions commonly used by SELinux Policy Editor
"""
import sys
import os
import string
from xml.dom.minidom import parse, parseString

def getAttr(node, attrName):
    """
    get attribute value, |attrName| is name of attribute
    """
    attr=""
    for (name, value) in node.attributes.items():
        if(name == attrName):
            attr = value
    return attr


def readXML(filename):
    """
    Parse XML file, return DOM document
    """
    try:
        fh = open(filename)
    except:
        sys.stderr.write("Input file open error:%s" % filename)
        sys.exit(1)

    try:
        domdoc = parseString(fh.read())
            
    except:
        fh.close()
        sys.stderr.write("XML Parse Error: %s" % filename)
        sys.exit(1)
            
    fh.close()
    return domdoc

#This stores path to configs
gConf = {'cross_flag': False ,
         'all.sp' : '/etc/seedit/policy/all.sp',
         'sppath' : '/etc/seedit/policy/',
         'guipath' : '/usr/sbin/',
         'generated.conf': '/usr/share/seedit/sepolicy/generated.conf',
         'seedit-load' : '/usr/sbin/seedit-load',
         'seedit-load.conf' : '/usr/share/seedit/seedit-load.conf',
         'converter.conf': '/usr/share/seedit/base_policy/converter.conf',
         'spdl_spec.xml': '/usr/share/seedit/base_policy/spdl_spec.xml'
         }

def readSeeditConf():
    files = ("./seedit.conf", "/usr/share/seedit/seedit.conf")
    conf = ""
    for f in files:
        if os.path.exists(f):
            conf = f
    
    if conf == "":
        return

    try:
        input = open(conf, 'r')
    except:
        print "File Open Error:"+conf+"\n"  
    lines = input.readlines()
    for line in lines:
        list = string.split(line)
        try:
            gConf[list[0]] = list[1]
        except:
            print  "Error in seedit.conf:"+line
    input.close()
  

 
readSeeditConf()

gGeneratedPolicy=gConf['generated.conf']
#Path to converter.conf
gConverterConf=gConf['converter.conf']
#Path to spdl_spec.xml
gSpecXML=gConf['spdl_spec.xml']
if gConf['cross_flag'] == "true":
    gCross = True
else:
    gCross = False

gSeeditLoadConf=gConf['seedit-load.conf']
gSPPath=gConf["sppath"]
gAllsp=gConf["all.sp"]
gSeedit_load= gConf["seedit-load"]
gGeneratedPolicy=gConf["generated.conf"]
gGUIPath = gConf["guipath"]

