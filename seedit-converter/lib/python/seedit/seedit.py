
"""
Functinos commonly used by SELinux Policy Editor
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

