#!/usr/bin/python
# Author: Yuichi Nakamura <ynakam@gwu.edu>
# Copyright (c) 2006 Yuichi Nakamura
# License: GPL

"""
This imports xml SPDL file to SPDL syntax

"""

from xml.dom.minidom import parse, parseString
import os
import sys
import string
import re
import getopt
sys.path.insert(0,"/usr/lib")
from seedit.seedit import getAttr, readXML


def errorExit(msg):
    sys.stderr.write(msg)
    sys.exit(1)
    return

def printUsage():
    sys.stderr.write("audit2spdl [-i <inputfile> ] [-o <output dir>]\n")
    sys.stderr.write("\t-i\tread input from <inputfile>\n")
    sys.stderr.write("\t-o\toutput result to directory\n")
    sys.exit(1)



def tagListToAttrStr(tagList,attrName,sep=","):
    #attrName:"value" is exceptional,..should be fixed in the future
    str=""
    for tag in tagList:
        if str=="":
            if attrName=="value":
                str = tag.firstChild.data
            else:
                str = getAttr(tag,attrName)
        else:
            if attrName=="value":
                str = str+sep+tag.firstChild.data
            else:
                str=str+sep+getAttr(tag, attrName)

    re.sub(",$","",str)

    return str

def tagNameToAttrStr(node, tagName, attrName):
    tag = node.getElementsByTagName(tagName)    
    return tagListToAttrStr(tag,attrName)
    
def programToSPDL(tag,output):
    output.write("program ")
    output.write(tagNameToAttrStr(tag,"path","value")+";\n")

def domain_transToSPDL(tag,output):
    output.write("domain_trans ")
    output.write(tagNameToAttrStr(tag,"parentdomain","value")+" ")
    output.write(tagNameToAttrStr(tag,"entrypoint","value"))
    output.write(";\n")

def allownetToSPDL(tag,output):
    output.write("allownet ")

    protocol = tagNameToAttrStr(tag, "protocol","value")
    port = tagNameToAttrStr(tag, "port","value")
    node = tagNameToAttrStr(tag, "node","value")
    netif = tagNameToAttrStr(tag, "netif","value")
    domain = tagNameToAttrStr(tag, "domain", "value")
    permission = tagNameToAttrStr(tag, "permission", "value")
    output.write("-protocol "+protocol+" ")
    if(port):
        output.write("-port "+port)
    if(domain):
        output.write("-domain "+domain)
    if(netif):
        output.write("-netif "+netif)
    if(node):
        output.write("-node "+node)
    output.write(" "+permission)
    output.write(";\n")

def allowcomToSPDL(tag,output):
    option=tagNameToAttrStr(tag,"option","value")
    domain=tagNameToAttrStr(tag,"domain","value")
    permission=tagNameToAttrStr(tag,"permission","value")
    if permission:
        output.write("allowcom -%s %s %s;\n" %(option,domain,permission))
    else:
        output.write("allowcom -%s %s;\n" %(option,domain))
        
def allowprocToSPDL(tag,output):
    option=tagNameToAttrStr(tag,"option","value")
    permission=tagNameToAttrStr(tag,"permission","value")
    output.write("allowproc -%s %s;\n" %(option,permission))


def allowdevToSPDL(tag,output):
    rule = tag.nodeName
    option=tagNameToAttrStr(tag,"option","value")
    path=tagNameToAttrStr(tag,"path","value")
    if path:
        output.write("%s -%s %s;\n" %(rule,option,path))
        return
    role = tagNameToAttrStr(tag,"role","value")
    permission=tagNameToAttrStr(tag,"permission","value")
    if role:
        output.write("%s -%s %s %s;\n" %(rule,option,role,permission))
    else:
        output.write("%s -%s %s;\n" %(rule,option,permission))
    
def allowprivToSPDL(tag,output):
    rule = tag.nodeName
    type = getAttr(tag,"type")
    if type=="deny":
        rule =  re.sub("^allow","deny",rule)

    option=tagNameToAttrStr(tag,"option","value")
    output.write("%s %s;\n" %(rule,option))

def userToSPDL(tag,output):
    user = tagNameToAttrStr(tag,"uname","value")

    output.write("user %s;\n" % user)

def includeToSPDL(tag,output):
    str = tagNameToAttrStr(tag, "path", "value")
    output.write("include %s;\n" % str)

def allowfsToSPDL(tag,output):
    if(getAttr(tag,"type")=="allow"):
        fs = tagNameToAttrStr(tag, "fs","value")
        permission=tagNameToAttrStr(tag,"permission","value")
        output.write("allowfs %s %s;\n" %(fs,permission))
    elif(getAttr(tag,"type")=="exclusive"):
        fs = tagNameToAttrStr(tag, "fs","value")
        label=tagNameToAttrStr(tag,"label","value")
        output.write("allowfs %s exclusive %s;\n" %(fs,label))

def allowtmpToSPDL(tag,output):
    fs = tagNameToAttrStr(tag, "fs","value")
    dir = tagNameToAttrStr(tag,"dir","value")
    name =tagNameToAttrStr(tag,"name","value")
    permission = tagNameToAttrStr(tag, "permission", "value")
    output.write("allowtmp ")
    if fs:
        output.write("-fs %s " % fs)
    if dir:
        output.write("-dir %s " % dir)
    if name:
        output.write("-name %s " % name)
    if permission:
        output.write("%s" % permission)
    output.write(";\n")


def allowfileToSPDL(tag,output):

    type = getAttr(tag,"type")

    if type=="allow":
        output.write("allow ")
    elif type=="deny":
        output.write("deny  ")     
    else:
        sys.stderr.write("Error! in tag allowfile")
        sys.exit(1)

        
    output.write(tagNameToAttrStr(tag,"path","value"))
    if(type!="deny"):
        output.write(" ")
    output.write(tagNameToAttrStr(tag,"permission","value")+";\n")

def allowtmpToSPDL(tag, output):

    type = getAttr(tag,"type")
    output.write("allowtmp ")

    s = tagNameToAttrStr(tag,"dir","value")
    if s:
        output.write("-dir "+s+" ")
    else:
        s = tagNameToAttrStr(tag,"fs","value")
        if s:
            output.write("-fs "+s+" ")
        else:
            sys.stderr.write("Error allowtmp\n")
            exit(1)

    s = tagNameToAttrStr(tag,"name","value")
    output.write("-name "+s+" ")

    permission = tagNameToAttrStr(tag, "permission", "value")
    output.write(permission+";\n")


def sectionToSPDL(section, output):
    """
    convert between <section>...</section> to SPDL
    """

    output.write("{\n")
    if(getAttr(section,"type")=="domain"):
        output.write("domain ");
    else:
        output.write("role ");
    output.write(getAttr(section,"id")+";\n")

    for child in section.childNodes:
        #Comment 
        ruleName = child.nodeName
        if ruleName !="comment" and ruleName !="#text":
            commentList = child.getElementsByTagName("comment")
            if commentList:
                comment = commentList[0]
                if comment.firstChild:
                    output.write(comment.firstChild.data)
                    
        if ruleName == "domaintrans":
            domain_transToSPDL(child, output)
        elif ruleName =="allowfile":
            allowfileToSPDL(child,output)
        elif ruleName=="allownet":
            allownetToSPDL(child,output)
        elif ruleName=="allowcom":
            allowcomToSPDL(child,output)
        elif ruleName=="allowproc":
            allowprocToSPDL(child,output)
        elif ruleName=="allowdev":
            allowdevToSPDL(child,output)
        elif ruleName=="allowpriv":
            allowprivToSPDL(child,output)
        elif ruleName == "allowfs":
            allowfsToSPDL(child,output)
        elif ruleName == "user":
            userToSPDL(child,output)
        elif ruleName == "program":
            programToSPDL(child,output)
        elif ruleName =="allowtmp":
            allowtmpToSPDL(child,output)
        elif ruleName =="comment":
            if child.firstChild:
                if not re.search("^[\s]+$", child.firstChild.data):
                    output.write(child.firstChild.data)
        elif ruleName =="include":
            includeToSPDL(child,output)
        elif ruleName =="#text":
            pass
        else:
            print ruleName+"is not supported yet, wait"
    
    output.write("}\n")
    
    return

    


def toSPDL(domdoc, outdir):
    sectionList = domdoc.getElementsByTagName("section")
    
    for section in sectionList:
        output=sys.stdout
        if(outdir):
            domain = getAttr(section,"id")
            if(domain !="global"):
                filename = outdir+"/"+domain+".sp"
            else:
                filename = outdir+"/"+domain
            try:
                output=open(filename,"w")
            except:
                sys.stderr.write("Warning:Output File %s open error\n" % filename)
        sectionToSPDL(section,output)
        
    return

#################
#Main function
#############
try:
    opts, args = getopt.getopt(sys.argv[1:], "i:o:", ["input=","outdir"])
except getopt.GetoptError:
    printUsage()

xmlFile=""
outdir=""

for opt,arg in opts:
    if opt in ("-i", "--input"):
        try:
            xmlFile=arg
        except:
            errorExit("Input file open error:"+arg+"\n")
    if opt in ("-o","--outdir"):
        outdir=arg
            

domdoc=readXML(xmlFile)
toSPDL(domdoc,outdir)


 



