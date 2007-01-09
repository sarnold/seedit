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

