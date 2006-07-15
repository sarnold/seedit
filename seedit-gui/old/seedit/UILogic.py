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
from xml.dom.minidom import parse, parseString
SEEDIT_ERROR="error"
SEEDIT_SUCCESS="success"
SEEDIT_INFO="info"

##for allowtype
NO_CONFIG=0
ALLOW_LOCAL=1
ALLOW_GLOBAL=2
DENY_LOCAL=4
DENY_GLOBAL=8

###checkbox state
CHECKED=1
UNCHECKED=0
HIDDEN=2


class seeditDataHolder(object):
    """
    Singleton that hold UI Data
    """
    # mPolicy : seeditPolicy instance, to hold policy document etc.
    
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type.mPolicy = seeditPolicy()
            type._the_instance = object.__new__(type)
        return type._the_instance

    def getPolicy(self):
        return self.mPolicy

class seeditPolicy:
    """
    hold policy and its related attribute, functions
    """
    # mPolicyDoc XML policy document
    # mPolicFileName policy filename 
    # mSectionTags dictionaly of sectiontags, should be updated in domain delete/add
    # mModified: modifed but unsaved document, True
    
    def __init__(self,parent=None):
        self.mPolicyDoc = None
        self.mPolicyFileName = None 
        self.mSectionTags = None
        self.mModified = False
    def setPolicyDoc(self,d):
        if(self.mPolicyDoc):
            self.mPolicyDoc.unlink()
        else:
            self.mPolicyDoc = d
    def getPolicyDoc(self):
        return self.mPolicyDoc

    def setPolicyFileName(self,d):
        self.mPolicyFileName = d
    def getPolicyFileName(self):
        return self.mPolicyFileName

    def getModified(self):
        return self.mModified

    def savePolicy(self, filename):
        """
        save mPolicyDoc to filename
        return (status, message)
        """
        xmldoc = self.mPolicyDoc
        if filename==None or xmldoc==None:
            message = _("Policy is not load yet")
            return (SEEDIT_ERROR, message)
        try:
            outfp = open(filename, 'w')
            xmldoc.writexml(outfp)
            outfp.close()
            message = _("Policy Saved to %s") % filename
            self.mModified = False
            return (SEEDIT_SUCCESS,message)
        except Exception,e:
            message = _("Policy Save error.Filename:%s\n Detail:%s") % (filename,e)
            return (SEEDIT_ERROR, message)
        
        
    def openPolicy(self, filename):
        """
        open PolicyFile pointed by filename
        return (status, message)    
        """
        try:
            self.mPolicyDoc = readXML(filename)
        except Exception, e:
            message = _("Policy File open Error\n Filename: %s\nDetail:%s") % (filename, e)
            self.mPolicyFileName=None
            return (SEEDIT_ERROR,message)

        self.mPolicyFileName=filename

        self.mSectionTags = dict()
        domains = self.mPolicyDoc.getElementsByTagName("section")
        for domain in domains:
            id = getAttr(domain, "id")
            self.mSectionTags[id] = domain
            
        return (SEEDIT_SUCCESS, "")


    def getSectionTag(self,name):
        if self.mSectionTags.has_key(name):
            return self.mSectionTags[name]
        return None
    
    def getDomainList(self):
        if self.mPolicyDoc == None:
            return None
        domainList = []
        sectionList = self.mPolicyDoc.getElementsByTagName("section")
        for section in sectionList:
            d = getAttr(section, "id")
            if d:
                domainList.append(d)
        return domainList
    
    def getDomainInfo(self, domain):
        """
        return (List of entrypoint, comment)
        """
        entryPointList = []
        comment =""
        
        print domain
        domainRoot = self.getSectionTag(domain)
        if domainRoot == None:
            return None        
        
        entryPoints = domainRoot.getElementsByTagName("entrypoint")
        for entry in entryPoints:
            entryPointList.append(getValue(entry))

        childs = domainRoot.childNodes
        for child in childs:
            if child.nodeName == "comment":
                if child.firstChild:
                    comment = child.firstChild.data
                break           

        return (entryPointList, comment)

    def getAllowPriv(self, domain):
        #key: option
        #value: allowtype
        allowPriv=dict()
        
        root = self.getSectionTag(domain)
        if root==None:
            return None
        tags = root.getElementsByTagName("allowpriv")
        if tags == None:
            return None

        for tag in tags:
            type = getAttr(tag,"type")
            option = getOption(tag)
            print type+option
            if type=="allow":
                if  allowPriv.has_key(option):
                    allowPriv[option]=allowPriv[option]|ALLOW_LOCAL
                else:
                    allowPriv[option]=ALLOW_LOCAL                
            else:
                if allowPriv.has_key(option):
                    allowPriv[option]=allowPriv[option]|DENY_LOCAL
                else:
                    allowPriv[option]=DENY_LOCAL

        root = self.getSectionTag("global")
        tags = root.getElementsByTagName("allowpriv")
        if tags:
            for tag in tags:
                type = getAttr(tag,"type")
                option = getOption(tag)
                print type+option
                if type=="allow":
                    if  allowPriv.has_key(option):
                        allowPriv[option]=allowPriv[option]|ALLOW_GLOBAL
                    else:
                        allowPriv[option]=ALLOW_GLOBAL
                else:
                    if allowPriv.has_key(option):
                        allowPriv[option]=allowPriv[option]|DENY_GLOBAL
                    else:
                        allowPriv[option]=DENY_GLOBAL        
        return allowPriv

#####
###Normal functions
def getValue(node):
    if node.firstChild == None:
        return ""
    value =  node.firstChild.data
    if value==None:
        return ""
    return value

def getAttr(node, attrName):
    """
    get attribute value, |attrName| is name of attribute
    """
    attr=""
    for (name, value) in node.attributes.items():
        if(name == attrName):
            attr = value
    return attr

def getOption(node):
    result =[]
    tags = node.getElementsByTagName("option")
    
    value = getValue(tags[0])

    return value


def readXML(file):
    try:
        fh = open(file)
    except:
        raise
    try:
        domdoc = parseString(fh.read())
    except:
        fh.close()
        raise
    fh.close()
    return domdoc


def allowTypeToCbValue(allowType,denySupport):
    """
    Convert allowType to Check Box value
    |denySuport| is whether denyxxx is supported or not
    """
    if  denySupport:
        if allowType & DENY_LOCAL:
            return UNCHECKED
        elif allowType & ALLOW_LOCAL:
            return CHECKED
        elif allowType & ALLOW_GLOBAL:
            return CHECKED
    else:
        if allowType & DENY_LOCAL:
            return UNCHECKED
        elif allowType & ALLOW_GLOBAL:
            return HIDDEN
        elif allowType & ALLOW_LOCAL:
            return CHECKED

    return None
        
    
