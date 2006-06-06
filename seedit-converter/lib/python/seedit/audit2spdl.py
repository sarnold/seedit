#!/usr/bin/python
# Author: Yuichi Nakamura <ynakam@gwu.edu>
# Copyright (c) 2006 Yuichi Nakamura
# License: GPL

from xml.dom.minidom import parse, parseString
import os
import sys
import string
import re
import getopt
import gettext
from seedit import getAttr
from stat import *

def errorExit(msg):
    sys.stderr.write(msg)
    sys.exit(1)
    return


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

def getInput(opts):
    input=sys.stdin

    for opt,arg in opts:
        if opt in ("-d", "--dmesg"):
            try:
                input=os.popen("dmesg", "r")
            except:
                errorExit("/bin/dmesg can not be used\n")
        if opt in ("-i", "--input"):
            try:
                input=open(arg, "r")
            except:
                errorExit("Input file open error:"+arg+"\n")
        if opt in ("-a","--audit"):
            try:
                input = os.popen("/sbin/ausearch -m avc,daemon_start")
            except:
                errorExit("Warning ausearch is not available for your system input is /bin/dmesg")
                try:
                    input=os.popen("dmesg", "r")
                except:
                    errorExit("/bin/dmesg can not be used\n")

                
    return input


def getPid(line):
    """
    get Pid from log entry
    """

    m=re.compile("\spid=\d+").search(line)
    if m:
        pid = string.split(m.group(),"=").pop()
        return pid

    return -1

def getInode(line):
    m=re.compile("\sino=\d+").search(line)
    if m:
        ino = string.split(m.group(),"=").pop()
        return string.atoi(ino)
    return -1

def getName(line):
    m=re.compile("\sname=\".+\"").search(line)
    if m:
        name = string.split(m.group(),"=").pop()
        name = string.replace(name,"\"","")
        return name
    m=re.compile("\spath=\".+\"").search(line)
    if m:
        name = string.split(m.group(),"=").pop()
        name = string.replace(name,"\"","")
        return name
    return ""

def getAuditId(line):
    """
    get Audit event ID in log entry
    """
    m = re.compile("audit\(\d+\.\d+:\d+").search(line)
    if m:
        id = string.split(m.group(),":").pop()
        return id
    else:
        return None
    
    return None


def guessPathByLocate(line):
    """
    Guess path by locate command
    """
    ino = getInode(line)
    name = getName(line)
    comm = "locate "+name
    
    result=os.popen(comm)
    locates = result.readlines()
    for path in locates:
        path = string.replace(path,"\n","")
        try:
            s = os.lstat(path)
            if ino==s[1]:
                return path
            
        except:
            pass
    return ""


def guessPathByAusearch(line):

    """
    First, guess full path by ausearch.
    And return guessed path
    If not exist file is returned, notexist_|filename| is returned
    Can not be guessed, "" is returned
    """
    id = getAuditId(line)
    pid = getPid(line)
    if(id):
        try:
            result=os.popen("ausearch -a "+id+" -p "+pid+" 2>&1", "r")
            l=result.readline()

            path =""
            while l:
                if(string.find(l,"type=PATH")>=0 or string.find(l,"type=AVC_PATH")>=0):
                    m=re.compile("name=\S+").search(l)
                    if (m==None):
                        m = re.compile("path=\S+").search(l)
                    
                    if m:
                        path = string.split(m.group(),"=").pop()
                        path = string.replace(path,"\"","")
                        #path is got from type=PATH/AVC_PATH entry now..
                        #Let's check file exist..
                        try:
                            os.stat(path)
                            return path                            
                        except:
                            #path ="notexist_"+path
                            return ""
                    else:                        
                        return ""                    
                l=result.readline()

                if path==".":
                    return ""
                
            return path
            
        except:
            #ausearch not available
            return ""
           
    else:
        #audit event id is not available..
        return ""

    return ""

def makePathFromType(type):
    type = re.sub("^dir_","", type)
    path = string.replace(type,"_t","")
    path=string.replace(path,"_","/")
    path = "/"+path
    try:
        os.stat(path)
    except:
        #return "notexist_"+path
        return ""
    return path
    

def guessFilePath(rule,line):
    """
    guess full path information
    """

    if rule["type"] in gExcLabelList:
        return rule["type"]
    
    path= guessPathByAusearch(line)
    if path =="":
        #print "#Path can not be guessed from ausearch"
        path = guessPathByLocate(line)
        if path =="":
            path=makePathFromType(rule["type"])
        return path
    else:
        return path
    


def matchPermTagList(perm,secclass,permTagList):
    """
    find <permission> tag lists from |permTagList|
    whose value is |perm| and its neighboring <secclass> value is |secclass|
    """
    
    matchedPermTagList=[]
    for permTag in permTagList:            
        if (perm == getAttr(permTag,"value")):
            secclassTagList=permTag.parentNode.getElementsByTagName("secclass")
            secclassList=[]
            for tag in secclassTagList:
                secclassList.append(getAttr(tag,"value"))
                
            if secclass in secclassList:              
                matchedPermTagList.append(permTag)

    return matchedPermTagList


def appendResult(list, str):
    if str not in list:
        list.append(str)
    return list

def findFilePermission(doc,rule,allowtype):
    """
    find file permission using specification in XML
    |security| is security level of outputted policy, high or low can be specified
    """
    result=[]
    security = "low"

    if gHighSecurityFlag==True:
        security ="high"

    if security=="high":
        if rule["secclass"]=="dir" and "write" in rule["permission"]:
            result = appendResult(result, "dummy")
            return result
    
    integrateTagList=doc.getElementsByTagName("integrate")
    allowfileNode=None
    for integrateTag in integrateTagList:
        if(getAttr(integrateTag,"value")==allowtype):
            allowfileNode=integrateTag
            break

    permTagList=allowfileNode.getElementsByTagName("permission")
    permList=rule["permission"]
    secclass=rule["secclass"]
    
    for perm in permList:
        matchedPermTagList=matchPermTagList(perm, rule["secclass"], permTagList)
        for matchedPermTag in matchedPermTagList:
            if checkInternal(matchedPermTag,doc):
                continue
            optionNode= matchedPermTag.parentNode.parentNode.parentNode
   
            if allowtype=="allowtty" or allowtype=="allowpts":
                option=getAttr(optionNode,"value")
                if option not in result:
                    result.append(option)
            else:
                p = getAttr(optionNode,"value")
                if (security=="low"):
                    if p in ("o","e","c","t","a"):
                        continue  
                if (security=="high"):
                    if(p=="w"):
                        continue
                
                if p not in result:
                    result.append(p)
                    if p in ("w", "x","o", "a", "c", "e"):
                        result = appendResult(result, "r")
                        result = appendResult(result, "s")
                    if p == "r":
                        result = appendResult(result, "s")                  
                        

    return result
                        


def genAllowfs(rule,domdoc):
    """
    return Dict
    ruletype:   type of SPDL element, this case, allowfs
    domain:     domain
    fsname: name of filesystem
    permission: list of permission     
    """
    spRuleList=[]
    
    spRule= dict()
    spRule["ruletype"]="allowfs"
    spRule["domain"]= rule["domain"]
    
    if rule["type"] in gDomainList:
        if rule["domain"]==rule["type"]:
            spRule["fsname"]="proc_pid_self"
        else:
            spRule["fsname"]="proc_pid_other" 
    else:
        spRule["fsname"] = string.replace(rule["type"],"_t","")

    permList = findFilePermission(domdoc,rule,"allowfile")
    if not permList:
        permList = findFilePermission(domdoc,rule,"allowdev")
    
    spRule["permission"] = permList

    spRuleList.append(spRule)

    if permList:
        return spRuleList
    else:
        return None
    

def genFileAllow(rule,line,domdoc):
    """
    return Dict
    ruletype:   type of SPDL element, this case, allowfile
    domain:     domain
    path:       full path
    name:       only file name not fullpath
    permission: list of permission     
    """
    spRuleList=[]
    spRule = dict()    
    path = guessFilePath(rule,line)
    permList = findFilePermission(domdoc,rule,"allowfile")
    if not permList:
        permList = findFilePermission(domdoc,rule,"allowdev")
    if not permList:
        return []

    if rule["type"] == "security_t":
        return None

    spRule["ruletype"]="allowfile"
    spRule["domain"]=rule["domain"]
    spRule["name"]=rule["name"]
    ##make grab
    if rule["secclass"] == "dir":
        pass    
    elif os.path.islink(path):
        pass
    elif os.path.isdir(path):
        path = path + "/*"
    #convert /home -> ~/
    if re.search("^/home/", path):
        path = re.sub("/home/[^/]+","~",path)

    spRule["path"] = path
    if not os.path.isdir(path):
        permList = appendResult(permList,"r");

    spRule["permission"] = permList

    spRuleList.append(spRule)
    
    return spRuleList

def checkInternal(permissionTag,domdoc):
    """
    This is to avoid to output SPDL rules that is internally used
    check parent <option> tag for <permission>
    if <option internal="yes" return True
    """    
    n = findParentTag(permissionTag,domdoc,"option")
    
    if getAttr(n,"internal")=="yes":
        return True

    if getAttr(permissionTag,"nomatch")=="yes":
        return True

    return False

def findParentTag(node,domdoc,tagName):
    """
    find parent  tag  named |tagName| for |node|
    """
    while  node is not domdoc  and node.nodeName!=tagName:
        node = node.parentNode

    if node is domdoc and node.nodeName!=tagName:
        return None
    
    return node

    
def genExceptionalRule(rule,line,domdoc):
    """
    Generate rules, that can not be obtained from spdl_spec.xml file
    """
    
    spRuleList=[]
    
    
    #allowpriv unlabel
    if rule["type"] in gUnlabeledTypes:
        oneRule=dict()
        oneRule["domain"]=rule["domain"]
        oneRule["type"]=rule["type"]
        oneRule["ruletype"]="allowpriv"
        oneRule["option"]="unlabel"
        oneRule["suboption"]=""
        spRuleList.append(oneRule)

    return spRuleList

def genAllownet(rule,line,domdoc):
    """
    return list of Dict
    dict represents spdl rule to be outputted
    ruletype:   type of SPDL element, defined in <integrate value=
    domain:     domain
    type: type
    option:    <option value=
    suboption:  <option suboption=
    src: source port number
    dest: dest port number
    """
    spRuleList=[]

    integrateTagList=domdoc.getElementsByTagName("integrate")
    permTagList=[]
    for t in integrateTagList:
        ruleName=getAttr(t,"value")
        if ruleName =="allownet":
            permTagList.extend(t.getElementsByTagName("permission"))


    for perm in rule["permission"]:  
        list=matchPermTagList(perm,rule["secclass"],permTagList)
        if list:
            for l in list:
                if checkInternal(l,domdoc):
                    continue

                oneRule = dict()
                oneRule["ruletype"]="allownet"
                oneRule["domain"]=rule["domain"]
                oneRule["type"]=rule["type"]
                oneRule["permission"] =perm
                n=findParentTag(l,domdoc,"option")
                if n==None:
                    oneRule["option"]=""
                    oneRule["suboption"]=""
                else:
                    option = getAttr(n,"value")
                    oneRule["option"]= option
                    oneRule["suboption"]=getAttr(n,"suboption")
                    src = getEqualValue(line,"src")
                    dest = getEqualValue(line,"dest")
                    oneRule["src"]= src
                    oneRule["dest"] = dest
                    
                    if option=="net" and src!="": 
                        if int(src) < 1024 and getAttr(l,"value")=="name_bind":
                            continue
                spRuleList.append(oneRule)
    
    return spRuleList  


def printResult(outList):

    ## to avoid suggesting same rules
    # key: filename+rule
    # value List of tuple (filename, line, rule)
    outputStr = dict()
    for l in outList:

        (filename, line, rule) = l
    #    sys.stdout.write(_("#SELinux deny log:\n%s") % line)
     #   sys.stdout.write(_("#Suggested configuration\n"))
     #   sys.stdout.write(_("File %s: \n%s\n") %(filename, rule))
        key = filename+rule

        if not outputStr.has_key(key):
            outputStr[key]=[]
        outputStr[key].append((filename,line,rule))
  
       

    for key in outputStr.keys():
        list=outputStr[key]
        sys.stdout.write("-------------------------\n")
        sys.stdout.write(_("#SELinux deny log:\n"))
        for l in list:
            (filename, line, rule) = l
            sys.stdout.write("%s" % line)
        sys.stdout.write(_("#Suggested configuration\n"))
        sys.stdout.write(_("File %s: \n%s\n") %(filename, rule))
        sys.stdout.write("-------------------------\n\n")
            
def outputResult(outputDir,outputFileFlag,outList,verbose):

    #key: filename
    #value List of tuple (line, rule)
    outputStr = dict()
    
    #sort by filename
    for l in outList:
        (filename, line, rule) = l
        if not outputStr.has_key(filename):
            outputStr[filename]=[]
        outputStr[filename].append((line,rule))

    for file in outputStr.keys():

        output=sys.stdout
        output.write("####"+file+"\n")
        list=outputStr[file]
        for l in list:
            (line, rule)=l
            if verbose:
                output.write("#Log\n"+line+"#Rule\n")
            output.write(rule+"\n")
        output.write("###End of %s\n\n" % file)

    
    if outputFileFlag:
        sys.stdout.write("Are you sure to add ? (y/[n]\n")
        line=sys.stdin.readline()
        if string.find(line,"y")==-1 and string.find(line,"Y")==-1:
            return
        sys.stdout.write("Saving..\n")
        for file in outputStr.keys():            
            #Output to file
            fullPath=outputDir+"/"+file
            try:
                exist=True
                os.stat(fullPath)
            except:
                exist=False
                sys.stderr.write("Warning:Output File %s does not exist.\n" % fullPath)
            if exist:
                fp = open(fullPath,"r")

                tmpFile=fullPath+".tmp"

                try:
                    outfp=open(tmpFile,"w")
                except:
                    sys.stderr.write("Warning:Output File %s open error\n" % tmpFile)

                buf=fp.readline()
                while string.find(buf,"}")==-1 and buf :
                    outfp.write(buf)
                    buf=fp.readline()
                    list=outputStr[file]
                for l in list:
                    (line,rule)=l
                    if verbose:
                        outfp.write("#Log\n#"+line)
                    if re.search("notexist_",rule):
                        outfp.write("#"+rule+"\n")
                    else:
                        outfp.write(rule+"\n")                    
                outfp.write("}\n")
                fp.close()
                outfp.close()
                os.rename(tmpFile,fullPath)
           
        
        
def genAllowttyPtsCommon(rule,domdoc,generalList,roleTypeList,ruletype):
    spRuleList=[]
    vcsList=["vcs_device_t"]
    
    if rule["type"] not in generalList and  rule["type"] not in roleTypeList and rule["type"] not in vcsList:
        return []

    integrateTagList=domdoc.getElementsByTagName("integrate")
    permTagList=[]
    for t in integrateTagList:
        ruleName=getAttr(t,"value")
        if ruleName == ruletype:
            permTagList.extend(t.getElementsByTagName("permission"))

    for perm in rule["permission"]:  
        list=matchPermTagList(perm,rule["secclass"],permTagList)
        if list:
            for l in list:
                if checkInternal(l,domdoc):
                    continue
                oneRule = dict()
                oneRule["ruletype"]=ruletype
                oneRule["domain"]=rule["domain"]
                if rule["type"] in generalList:
                    oneRule["target"]="general"
                if rule["type"] in vcsList:
                    oneRule["target"]="vcs"
                    ruletype="allowtty"
                else:
                    if ruletype=="allowtty":
                        oneRule["target"] = re.sub("_tty_device_t$","_r", rule["type"])
                    if ruletype=="allowpts":
                        oneRule["target"] = re.sub("_devpts_t$","_r",rule["type"])                                                 
                    
                permList = findFilePermission(domdoc,rule,ruletype)
                oneRule["permission"] = permList
                spRuleList.append(oneRule)
            
    return spRuleList

def genAllowtty(rule,line,domdoc):
    spRuleList=[]

    generalTtyTypeList=("devtty_t", "tty_device_t")
    roleTtyTypeList=[]
    for role in gRoleList:
        roleTtyTypeList.append(re.sub("_t$","", role)+"_tty_device_t")

    spRuleList= genAllowttyPtsCommon(rule,domdoc,generalTtyTypeList, roleTtyTypeList, "allowtty")

    return spRuleList
    
def genAllowpts(rule,line,domdoc):
    spRuleList=[]

    generalPtsTypeList=("devpts_t", "ptmx_t")
    rolePtsTypeList=[]
    for role in gRoleList:
        rolePtsTypeList.append(re.sub("_t$","", role)+"_devpts_t")

    spRuleList= genAllowttyPtsCommon(rule,domdoc,generalPtsTypeList,  rolePtsTypeList,"allowpts")
    return spRuleList

def genOther(rule,line,domdoc):
    """
    return list of Dict
    dict represents spdl rule to be outputted
    ruletype:   type of SPDL element, defined in <integrate value=
    domain:     domain
    type: type
    option:    <option value=
    suboption:  <option suboption=
    """
    
    spRuleList=[]
    genRuleType=["allowpriv","allownet","allowcom"]

    integrateTagList=domdoc.getElementsByTagName("integrate")
    permTagList=[]
    for t in integrateTagList:
        ruleName=getAttr(t,"value")
        if ruleName in genRuleType:
            permTagList.extend(t.getElementsByTagName("permission"))
    
    for perm in rule["permission"]:  
        list=matchPermTagList(perm,rule["secclass"],permTagList)
        if list:
            for l in list:
                if checkInternal(l,domdoc):
                    continue
                oneRule = dict()
                oneRule["domain"]=rule["domain"]
                oneRule["type"]=rule["type"]
                n=findParentTag(l,domdoc,"option")
                if n==None:
                    oneRule["option"]=""
                    oneRule["suboption"]=""
                else:
                    oneRule["option"]=getAttr(n,"value")
                    oneRule["suboption"]=getAttr(n,"suboption")
                    n=findParentTag(l,domdoc,"integrate")
                if n==None:
                    oneRule["ruletype"]=""
                else:
                    oneRule["ruletype"]=getAttr(n,"value")

                
                if  (oneRule["ruletype"],oneRule["option"]) in gNeglectRule:
                    continue
                
                spRuleList.append(oneRule)

    return spRuleList
    
def genSPDL(rule,line,domdoc):
    """
    generate SPDL based on rule.
    rule is dictionary in parseLine funct    
    """

    spRuleList=[]

    spRuleList = genExceptionalRule(rule,line,domdoc)
    if spRuleList:
        return spRuleList

    spRuleList = genAllowtty(rule,line,domdoc)
    if spRuleList:
        return spRuleList

    spRuleList = genAllowpts(rule,line,domdoc)
    if spRuleList:
        return spRuleList
    
    ##Memo:: allowfs exclusive is not supported now..
    if rule["type"] in gFsLabelList or rule["type"] in gDomainList:
        spRuleList= genAllowfs(rule,domdoc)
        if spRuleList:
            return spRuleList
    
    if rule["secclass"] in gFileClass:
        spRuleList= genFileAllow(rule,line,domdoc)
        if spRuleList:
            return spRuleList

    spRuleList=genAllownet(rule,line,domdoc)
    if spRuleList:
        return spRuleList
    
    #allowtty,allowpts is in progress
    ################!!!!!!!!!!In progress..........
    return genOther(rule,line,domdoc)


def getEqualValue(line,name):
    """
    get value like |name|=value from |line|
    """
    value=""
    m = re.compile(name+"=\S+").search(line)
    if m:
        list = string.split(m.group(),"=")
        value = list.pop()

    return value

  
def parseLine(line):
    """
    Parse one log line and make&return dictionary.
    Keys are following
    domain 
    type 
    secclass 
    permission : list of permission
    """

    avcFlag=False
    denyFlag=False
    rule = dict()
 
    tokenList = string.split(line)
    for token in tokenList:
        if token=="avc:" or token=="message=avc:":
            avcFlag = True
        if token=="denied":
            denyFlag=True
        if(avcFlag and denyFlag):
            break

    if (not avcFlag or not denyFlag):
        return None
    
    
    rule["domain"] = ""
    m = re.compile("scontext=\S+").search(line)
    if m:
        list = string.split(m.group(),":")
        rule["domain"] = list.pop()

    m = re.compile("tcontext=\S+").search(line)
    if m:
        list = string.split(m.group(),":")
        rule["type"] = list.pop()
       
        
    rule["secclass"] = getEqualValue(line,"tclass")

    rule["permission"] = []
    m = re.compile("{\s+.+\s+}").search(line)
    if(m):
        list = string.split(m.group())
        for l in list:
            if l!="}" and l!="{":
                rule["permission"].append(l)


    rule["name"] = getName(line)

    return rule


def getFsLabelList(converterConf):
    label=[]
    try:
        fp=open(converterConf,"r")
    except:
        errorExit("converter.conf open error:"+converterConf+"\n")

    line=fp.readline()
    while line:
        if(string.find(line,"supported_fs")>=0):
            list=string.split(line)
            list.pop(0)
            for l in list:              
                label.append(l+"_t")
        line=fp.readline()    
            
    fp.close()
    return label

def getDomainList(spPath):
    domainList=[]
    roleList=[]
    try:
        fp = open(spPath,"r")
    except:
        errorExit("Simplified Policy Open error:"+spPath+"\n")
    line = fp.readline()
    reg=re.compile("^\s*domain\s+\S+;")
    reg2=re.compile("^\s*role\s+\S+;")

    while line:
        m=reg.search(line)
        if m:
            str = string.replace(m.group(),";","")
            domainList.append(string.split(str).pop())
        else:
            m=reg2.search(line)
            if m:
                str = string.replace(m.group(),";","")
                str = re.sub("_r$", "_t", str)
                domainList.append(string.split(str).pop())
                roleList.append(string.split(str).pop())
        line=fp.readline()

    fp.close()
    return ( domainList, roleList)

def getExcLabelList(generatedPolicy):
    label=[]
    try:
        fp = open(generatedPolicy,"r")
    except:
        errorExit("Generated Policy Open error:"+generatedPolicy+"\n")

    line = fp.readline()
    reg=re.compile("^file_type_auto_trans\(.*")
    while line:
        m=reg.search(line)
        if m:
            str = string.replace(m.group(),")","")
            label.append(string.split(str,",").pop())
            
        line=fp.readline()
    
            
    fp.close()
    return label


def domainToRole(domain):
    """
    replace _r to _t when domain is domain for role(such as staff_t
    if domain is not domain for role, do nothing
    """
    if domain in gRoleList:
        domain = re.sub("_t$","_r", domain)

    return domain

def domainToFileName(domain):
    """
    Suggest filename where policy is added
    """
    fileName=""
    domain = domainToRole(domain)
 
    fileName=domain+".sp"
    return fileName

def permListToStr(permList):
    str = ""
    for perm in permList:
        str = str+ perm+","
    str= re.sub(",$","",str)
    return str

def allowTtyPtsStr(spRule):
    str=""
    ruletype=spRule["ruletype"]
    if(ruletype=="allowtty"):
        option="-tty"
    else:
        option="-pts"    
    prestr="allowdev "+option+" "+spRule["target"]
    permList=spRule["permission"]
    for perm in permList:
        str = str+prestr+" "+perm+";\n"
    
#    str = str+" "+permListToStr(permList)+";"
    return str

def allowfileStr(spRule):
    str=""

    if spRule["path"]=="":
        str = "allow "+spRule["name"]+" "
    else:
        str="allow "+spRule["path"]+" "
    permList=spRule["permission"]
    if "dummy" in permList:
        str = _("#allow:Nothing generated for safety\n")
        return str
    
    str = str+" "+permListToStr(permList)+";"
    
    path = spRule["path"]
    if path =="":
        str = "#"+str
        str = _("#Failed to generate, because failed to obtain fullpath.\n") +str
    return str
    

def allowfsStr(spRule):
    str=""

    str="allowfs "+spRule["fsname"]+" "
    permList=spRule["permission"]
    if "dummy" in permList:
        str = _("#allowfs:Nothing generated for safety\n")
        return str

    str = str+" "+permListToStr(permList)+";"
    return str


def allowcomStr(spRule,security="low"):
    str=""
    option = spRule["option"]
    if(security == "low"):
        if option!="sig":
            option = "ipc"
    
    str ="allowcom -"+option+" "+domainToRole(spRule["type"])
    suboption=spRule["suboption"]
    if suboption=="" and option!="sig":
        str = _("#allowcom, nothing generated from this log for safety")

    
    if suboption:
        str =str+" "+suboption

    str=str+";"
    return str

def allownetStr(spRule):
    str=""
    option=spRule["option"]
    src=""
    suboption=""
    
    if spRule["suboption"]:
        suboption = spRule["suboption"]
        src = spRule["src"]
        dest = spRule["dest"]
        
    if suboption=="client":
        port = dest
        if string.atoi(dest) > 1023:
            port = "1024-"
    if suboption =="server":
        port =src

    if spRule["option"] == "tcp":
        if suboption in ("server","client"):         
            if spRule["permission"] not in ("name_bind", "name_connect"):
                return  "# Nothing generated for safety"
            
    if suboption=="use":
        str ="allownet -protocol "+option+" "+suboption+";"    
    else:
        str ="allownet -protocol "+option+" -port "+port+" "+suboption+";"    
    return str

def allowprivStr(spRule):
    str=""
    str=spRule["ruletype"]+" "+spRule["option"]+";"
    return str    


def SPDLstr(spRuleList,line):
    """
    return list of
    (filename to be outputted, log entry, generated rule)
    """
    outStruct=[]
    for spRule in spRuleList:
        fileName = domainToFileName(spRule["domain"])

        ruleStr=""
        ruletype=spRule["ruletype"]
        if ruletype=="allowfile":
            ruleStr = allowfileStr(spRule)

        elif ruletype=="allowfs":
            ruleStr = allowfsStr(spRule)

        elif ruletype=="allowcom":
            ruleStr= allowcomStr(spRule)

        elif ruletype=="allownet":
            ruleStr = allownetStr(spRule)

        elif ruletype=="allowpriv":
            ruleStr = allowprivStr(spRule)            
        elif ruletype in ("allowpts","allowtty"):
            ruleStr=allowTtyPtsStr(spRule)
      
        outStruct.append((fileName,line,ruleStr))
      
    return outStruct

############
#####Main function

gFileClass = ["dir","file","lnk_file","sock_file", "fifo_file","chr_file","blk_file" ]

#Path to simplified policy
gSPPath="/etc/seedit/policy/all.sp"
#
gGeneratedPolicy="/etc/seedit/converter/sepolicy/generated.conf"
#Path to converter.conf
gConverterConf="/etc/seedit/converter/conf/base_policy/converter.conf"
#Path to spdl_spec.xml
gSpecXML="/etc/seedit/converter/conf/base_policy/spdl_spec.xml"
#labels defined by allow exclusive rule
gExcLabelList=getExcLabelList(gGeneratedPolicy)

#labels used for allowfs rule
gFsLabelList=getFsLabelList(gConverterConf)
#list of domain defined in SPDL
#Note that suffix of gRoleList is "_t" not "_r"
( gDomainList, gRoleList ) = getDomainList(gSPPath)

gRootNodeName="spdl"
#list of unlabeled types
gUnlabeledTypes=["unlabeled_t","file_t"]

gNeglectRule=[("allowpriv","unlabel"),("allowpriv","write"),("allowpriv","read"),("allowpriv","search"),("allowpriv","all")]

#-s option
gHighSecurityFlag=False

# -l option 
gLoadPolicyFlag=False
# -v option 
gVerboseFlag =False

gOutput="/etc/selinux/seedit/src/simplified_policy"
