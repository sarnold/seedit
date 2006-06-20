#!/usr/bin/python
# Author: Yuichi Nakamura <ynakam@gwu.edu>
# Copyright (c) 2005 Yuichi Nakamura
# License: GPL

"""
This generates macros and latex document based on SPDL specification XML file

"""


#import xml.dom.minidom
from xml.dom.minidom import parse, parseString
import sys
import string
import re
import getopt


def readSPDLSpec(filename):
    """
    Parse spdl spec XML file, return DOM document
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

def getAttr(node, attrName):
    """
    get attribute value, |attrName| is name of attribute
    """
    attr=""
    for (name, value) in node.attributes.items():
        if(name == attrName):
            attr = value
    return attr

def getAttList(attName, rootNode, nodeName):
    attList = []
    nodeList = rootNode.getElementsByTagName(nodeName)
    
    for node in nodeList:
        for (name, value) in node.attributes.items():
            if name == attName:
                attList.append(value)

    return attList
            
    

def makeRuleList(rulesNode):
    """
    process <rule> tag between <rules>  </rules>
    and make ruleList defined follows
    Element of ruleList is dictionary, keys are following
    disabled: (yes or no), if yes it is commented out
    domain: if |domain| it means individual domain
    type:  if |type| it means individual domain
    secclass: list of object class
    permission: list of permissions
    """
    ruleList = [] 
    ruleNodeList = rulesNode.getElementsByTagName("rule")
    if ruleNodeList == None:
        return None
    
    for ruleNode in ruleNodeList:
        rule = dict()
        #make rule["disabled"]
        rule["disabled"]="no"
        for (name, value) in ruleNode.attributes.items():
            rule[name]=value
        
        #make others
        domainNodeList = ruleNode.getElementsByTagName("domain")
        rule["domain"] = getAttList("value",ruleNode, "domain")
        rule["type"] = getAttList("value",ruleNode, "type")
        rule["secclass"] = getAttList("value",ruleNode, "secclass")
        rule["permission"] = getAttList("value",ruleNode, "permission")
                
        rule["domain"].sort()
        rule["type"].sort()
        rule["secclass"].sort()
        rule["permission"].sort()
        
        ruleList.append(rule)

    return ruleList


def braceList(list):
    """
    if list element is single return list[0]
    else brace list elements by "{" "}"
    """
    str=""
    if(len(list)==1):
        str = list[0]
        return str
    else:
        str = "{ "+ string.join(list) +" }"
    return str

def printRuleList(ruleList):
    """
    print ruleList
    """
    if ruleList == None:
        return
    for rule in ruleList:
        print "###one rule"
        for k,v in rule.iteritems():
            print k,string.join(v)

def escapeChar(str, char):
    str = string.replace(str,char,"\\"+char)
    return str
    

def printLatexTableBody(outFileObject,ruleList):
  for rule in ruleList:
        objList = rule["secclass"]
        permList = rule["permission"]
        domainList = rule["domain"]
        typeList = rule["type"]
        
        i =0 
        for obj in objList:
            obj = string.replace(obj,"_","\\_")
            if i < len(permList):
                perm = permList[i]
                perm = string.replace(perm,"_","\\_")
            else:
                perm =""
            if i< len(domainList):
                domain = domainList[i]
                domain = string.replace(domain,"_","\\_")
            else:
                domain =""
               
            if i< len(typeList):
                type = typeList[i]
                type = string.replace(type,"_","\\_")
            else:
                type =""
            

            i = i+1
            outFileObject.write("%s & %s & %s & %s\\\\ \n" % (obj,perm,domain,type))
        j=i
        for perm in permList[i:]:
            
            obj = ""
            perm = string.replace(perm,"_","\\_")
            if j< len(domainList):
                domain = domainList[j]
                domain = string.replace(domain,"_","\\_")
            else:
                domain =""
               
            if j< len(typeList):
                type = typeList[j]
                type = string.replace(type,"_","\\_")
            else:
                type =""
            outFileObject.write("%s & %s & %s & %s\\\\ \n" % (obj,perm,domain,type))
            j = j+1
        
        outFileObject.write("\\hline\n")

    

def printLatexTable(outFileObject, ruleList, title):
    """
    Print latex table based on ruleList
    """
    
    outFileObject.write("\\begin{table}[h]\n")
    outFileObject.write("\\caption{%s}\n" % title)
    outFileObject.write("\\begin{tabular}{|l|l|l|l|}\n")
    outFileObject.write("\\hline\n")
    outFileObject.write("Object class & Permission & Domain & Type\\\\ \n")
    outFileObject.write("\\hline\n")
    if ruleList!=None:
        printLatexTableBody(outFileObject, ruleList)

    outFileObject.write("\\end{tabular}\n")
    outFileObject.write("\\end{table}\n")
    

def typeNameToMacroArg(type):
    if(type=="domain"):
        return "$1"
    if(type=="type"):
        return "$2"
    if(type=="from"):
        return "$1"
    if(type=="entry"):
        return "$2"
    if(type=="to"):
        return "$3"
    if(type=="global"):
	return "domain"
    return type
   
    

def printAllow(outFileObject, ruleList):
    """
    print allow statement to outFileObject
    based on ruleList
    """
    if ruleList == None:
        return 
    for rule in ruleList:
        domainList =[]
        for d in rule["domain"]:
            domainList.append(typeNameToMacroArg(d))

        typeList =[]
        for t in rule["type"]:
            typeList.append(typeNameToMacroArg(t))
        
        domain = braceList(domainList)
        type = braceList(typeList)
        secclass = braceList(rule["secclass"])
        permission = braceList(rule["permission"])
       
        allowStr="allow %s %s:%s %s;\n" % (domain, type, secclass, permission)
        if(rule["disabled"]=="yes"):
            allowStr="#"+allowStr
           
        outFileObject.write(allowStr)

def printMacro(outFileObject, macroName, ruleList,comment):
    """
    Print macro used for converter based on |ruleList|
    |macroname| is name of macro
    |comment| is comment for macro
    """
    outFileObject.write("define(`%s',`\n" % macroName)
    if comment!="":
        outFileObject.write("%s" % comment)
    printAllow(outFileObject, ruleList)
    outFileObject.write("')\n\n")

def printUsage():
    """
    Print usage when command line option is wrong
    """
    print ("usage:%s [-lm] -i <file> -o <file>" % sys.argv[0])
    print "-i --input <file>  Input SPDL specification file"
    print "-m --mode latex|macro|unsupported|expand Specify output file type. If |latex|, latex is outputted, if |macro|, macro for converter is outputted. If |unsupported| allow statements for unsupported permission is outputted If |expand| expand macros used in xml document" 
    print "-o --output <file> Specify output filename. Default is stdout"    
    sys.exit(1)   

def getText(parentNode, tagName):
    nodeList = parentNode.getElementsByTagName(tagName)
    if nodeList:
        if nodeList[0].firstChild == None:
            return ""
        return nodeList[0].firstChild.data
    return ""

def genCoreMacro(outFileObject,doc,mode):
    """
    Generates core macros(such as all_file_class),from group tag
    """
    if(mode=="macro"):
        outFileObject.write("####Following macros are used to represent set of permissions, secclasses\n")
    
    groupNodeList = doc.getElementsByTagName("group")
    for groupNode in groupNodeList:
        name = getAttr(groupNode, "value")
        elementList =[]
        elementNodeList=groupNode.getElementsByTagName("element")
        for elementNode in elementNodeList:
            elementList.append(getAttr(elementNode,"value"))

        if(mode=="macro"):
            outFileObject.write("define(`%s',`{ " % name)
            for e in elementList:
                outFileObject.write("%s " % e)
            outFileObject.write("}')\n\n")
         
                              
def genAllowRule(outFileObject,ruleName, doc,mode):
    """
    Parse <integrate value=|ruleName|>...</integrate> and generates documents
    
    """

    ruleNode = None;
    integrateNodeList = doc.getElementsByTagName("integrate")
    for integrateNode in integrateNodeList:
        name = getAttr(integrateNode, "value")
        if (name == ruleName):
            ruleNode = integrateNode

    if(ruleNode == None):
        print("Error: Invalid argument for genAllowRule function")
        sys.exit(1)
            
    text = getText(ruleNode, "description")
    if mode == "latex":
        outFileObject.write("\\subsection{%s}\n" % text)
        text = getText(ruleNode, "moredescription")
        if text:
            outFileObject.write(text)
    if mode == "macro":
        outFileObject.write("##%s\n" % text)
    
    optionNodeList=ruleNode.getElementsByTagName("option")

    tabnum=0
    for optionNode in optionNodeList:

        rulesNode=(optionNode.getElementsByTagName("rules"))[0]
        ruleList = makeRuleList(rulesNode)
        macroNode=(optionNode.getElementsByTagName("macro"))[0]
        macroName = getAttr(macroNode, "value")

        if mode =="macro":
            comment = getText(optionNode,"macro")+ getText(optionNode,"comment")

            comment = string.replace(comment,"\n","")
            comment ="#"+comment+"\n"
            printMacro(outFileObject, macroName,ruleList,comment)

        if mode =="latex":
            comment = getText(optionNode,"comment")
            title ="Option:"+getAttr(optionNode,"value")
            subopt = getAttr(optionNode,"suboption")
            if(subopt!=""):
                title = title+" suboption:"+subopt
            if(comment!=""):
                title=title+","+comment
            title = escapeChar(title,"_")
            printLatexTable(outFileObject, ruleList,title)
            tabnum = tabnum +1

            if tabnum % 5 == 0:
                outFileObject.write("\\clearpage\n")
            
    if mode == "latex":
        outFileObject.write("\\clearpage\n")
    
def genUnsupported(outFileObject, doc, mode):
    """
    Parse <unsupported>...</unsupported> and generates documents    
    """
    
    nodeList = doc.getElementsByTagName("unsupported")
    unsupportedNode=nodeList[0]
    sectionNodeList=unsupportedNode.getElementsByTagName("section")

    text = getText(unsupportedNode, "description")
    if mode == "latex":
        outFileObject.write("\\section{%s}\n" % text)
    if mode == "unsupported":
        outFileObject.write("##%s\n" % text)
        
    for sectionNode in sectionNodeList:
        descriptionNodeList= sectionNode.getElementsByTagName("description")
        desc = descriptionNodeList[0].firstChild.data
        if(mode == "unsupported"):
            outFileObject.write("#%s\n" % desc)        
        
        rulesNode=(sectionNode.getElementsByTagName("rules"))[0]
        ruleList = makeRuleList(rulesNode)
        if mode == "unsupported":
            printAllow(outFileObject, ruleList)
        if mode == "latex":
            printLatexTable(outFileObject, ruleList,desc)

    if mode == "latex":
        outFileObject.write("\\clearpage\n")
    if mode == "unsupported":
        outFileObject.write("##End of unsupported permissions\n")

def getMacroElements(macro,doc):
    list=[]
    groupTagList=doc.getElementsByTagName("group")
    node=None
    for groupTag in groupTagList:
        if(getAttr(groupTag,"value")==macro):       
            node=groupTag
            break

    tagList=node.getElementsByTagName("element")
    for tag in tagList:      
        list.append(getAttr(tag,"value"))

    return list

def replaceTag(doc,tagname,macroList):
    tagList=doc.getElementsByTagName(tagname)
    for tag in tagList:
        if(getAttr(tag,"value") in macroList):
            macro = getAttr(tag,"value")
            
            elementList=getMacroElements(macro,doc)
            for element in elementList:
                newTag=doc.createElement(tagname)
                atr=doc.createAttribute("value")
                atr.nodeValue=element
                newTag.setAttributeNode(atr)
                tag.parentNode.insertBefore(newTag,tag)

            tag.parentNode.removeChild(tag)
            
def expandCoreMacro(outFileObject,doc):

    macroList=[]
    groupTagList=doc.getElementsByTagName("group")
    for groupTag in groupTagList:
        macroList.append(getAttr(groupTag,"value"))

    replaceTag(doc,"permission",macroList)
    replaceTag(doc,"secclass",macroList)
    
    permTagList=doc.getElementsByTagName("permission")
    for permTag in permTagList:
        if(getAttr(permTag,"value") in macroList):
            macro = getAttr(permTag,"value")
            
            elementList=getMacroElements(macro,doc)
            for element in elementList:
                newTag=doc.createElement("permission")
                atr=doc.createAttribute("value")
                atr.nodeValue=element
                newTag.setAttributeNode(atr)
                permTag.parentNode.insertBefore(newTag,permTag)

            permTag.parentNode.removeChild(permTag)

    doc.writexml(outFileObject)
    

########
#Main Function
#########

spdlFile=""
outFileObject=sys.stdout
mode=""

try:
    opts, args = getopt.getopt(sys.argv[1:], "i:m:o:", ["input=","mode=","output="])
except getopt.GetoptError:
    printUsage()

for opt,arg in opts:
    if opt in ("-i", "--input"):
        spdlFile=arg
    if opt in ("-m", "--mode"):
        mode =arg
        if(mode != "latex" and mode != "macro" and mode!= "unsupported" and mode!="expand"):
            printUsage()
    if opt in ("-o", "--output"):
        filename = arg
        try:
            outFileObject = open(filename, 'w')
        except:
            print "Output file open error %s" % filename
            sys.exit(1)


doc = readSPDLSpec(spdlFile)

if mode == "expand":
    expandCoreMacro(outFileObject,doc)
    sys.exit(0)


genUnsupported(outFileObject, doc, mode)
if mode == "macro":
        outFileObject.write("### Below macros are generated from spdl_spec.xml by genmacro.py\n")
if mode == "latex":
    outFileObject.write("\\section{Integrated permissions by SPDL}\n")
genCoreMacro(outFileObject,doc,mode)
genAllowRule(outFileObject,"allowfile", doc,mode)
genAllowRule(outFileObject,"allowdev", doc,mode)
genAllowRule(outFileObject,"allowtty", doc,mode)
genAllowRule(outFileObject,"allowpts", doc,mode)
genAllowRule(outFileObject,"allownet", doc,mode)
genAllowRule(outFileObject,"allowcom", doc,mode)
genAllowRule(outFileObject,"allowpriv", doc,mode)
genAllowRule(outFileObject,"transition", doc,mode)

outFileObject.close()
        
doc.unlink()


