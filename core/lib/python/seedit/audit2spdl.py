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

from xml.dom.minidom import parse, parseString
import os
import sys
import string
import re
import getopt
import gettext
from seedit import *
from stat import *
gMatchpathcon = "/usr/sbin/matchpathcon -n"
gAusearch = "/sbin/ausearch"

#key: inode, value:path
gInoPathDir = dict()


#key: inode, value:path
# stores inode and full path obtained from chdir syscall log
gChdirInoPathDir = dict()

#key: pid ,value:path
gChrootStatus = dict()


def clearDict():
    gInoPathDir.clear()
    gChdirInoPathDir.clear()


def errorExit(msg):
    sys.stderr.write(msg)
    sys.exit(1)
    return


# 
def popNum(buf):
    maxPop=4 #Max number of pop, if delim of auditlog is changed, all log is poped, so need max nunber of pop.
    result=1
    
    if len(buf)==0:
        return 0

    if len(buf)<4:
        maxPop=len(buf)

    for i in range(maxPop):
        line = buf[-1-i]
        if line[0] == '-': #Delim of auditlog
            break
        result = result + 1

    return result


'''
loadPolicyFlag is for -l option
'''
def readLog(input, loadPolicyFlag):
    lines=input.readlines()
    lineBuf=[]
    if loadPolicyFlag:
        reg = re.compile("avc:.*granted.*{.*load_policy.*}")
        reg2= re.compile("type=DAEMON_START.*auditd.*start")
        reg3 =re.compile("type=SYSCALL.*syscall=12")
    
        for line in lines:
            m3 = reg3.search(line)
            if m3:
                #Eleminate unneeded logs(syscall=12 for unconfined domains)
                if getSubjDomain(line) in ("unconfined_t", "system_crond_t"):
                    n = popNum(line) # Count number of related log
                    if  n > 0:
                        for lp in range(n):
                            linebuf.pop()
                    
                    continue            
            
            lineBuf.append(line)
            m = reg.search(line)
            m2 = reg2.search(line)
            if m or m2:
                del lineBuf
                lineBuf=[]
        del lines
        lines=lineBuf

    return lines








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
                input = os.popen("/sbin/ausearch -m avc,syscall,daemon_start")
            except:
                errorExit("Warning ausearch is not available for your system input is /bin/dmesg")
                try:
                    input=os.popen("dmesg", "r")
                except:
                    errorExit("/bin/dmesg can not be used\n")

                
    return input


def getDomain(line):
    """
    get domain from log entry
    """
    domain = ""
    m = re.compile("scontext=\S+").search(line)
    if m:
        list = string.split(m.group(),":")
        domain = list[2]
    
    return domain


def getSubjDomain(line):
    """
    get domain from log entry
    """
    domain = ""
    m = re.compile("subj=\S+").search(line)
    if m:
        list = string.split(m.group(),":")
        try:
            domain = list[2]
        except:
            domain =""
    return domain




def getPid(line):
    """
    get Pid from log entry
    """

    m=re.compile("\spid=\d+").search(line)
    if m:
        pid = string.split(m.group(),"=").pop()
        return pid

    return "-1"

def getInode(line):
    m=re.compile("\sino=\d+").search(line)
    if m:
        ino = string.split(m.group(),"=").pop()
        return string.atoi(ino)
    m=re.compile("\sinode=\d+").search(line)
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


def getUniqueAuditId(line):
    """
    get conbination of time and Audit event ID in log entry
    It is unique
    """
    m = re.compile("audit\(\d+\.\d+:\d+").search(line)
    if m:
        id = m.group()
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
    print "##Guessing fullpath by locate:%s" % (line)

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


#Get path name considering chroot
def getPathWithChroot(name, inode,pid, ppid):
    candidatePath=[]

    candidatePath.append(os.path.normpath(name))
    
    if gChrootStatus.has_key(pid) : #may chroot
        cpath = gChrootStatus[pid]+"/"+name
        candidatePath.append(os.path.normpath(cpath))


    if gChrootStatus.has_key(ppid):
        cpath = gChrootStatus[ppid]+"/"+name
        candidatePath.append(os.path.normpath(cpath))

    for c in candidatePath:
        if inode == getInodeByStat(c):
            return c
    
    return ""

# return all candidate path with chroot
def getCandidatePathWithChroot(name, inode,pid, ppid):
    candidatePath=[]
    candidatePath.append(os.path.normpath(name))
    
    if gChrootStatus.has_key(pid) : #may chroot
        cpath = gChrootStatus[pid]+"/"+name
        candidatePath.append(os.path.normpath(cpath))

    if gChrootStatus.has_key(ppid):
        cpath = gChrootStatus[ppid]+"/"+name
        candidatePath.append(os.path.normpath(cpath))

    return candidatePath

##Number of PATH Entry
def countPATHEntry(logs):
    i = 0
    for l in logs:        
        if(string.find(l,"name=")>=0 or string.find(l,"path=")>=0):
            i = i+1
    return i
             
##Guess full path from PATH Entry
def getPATHEntry(logs,inode):
    numPATH=countPATHEntry(logs)
    if numPATH==0:
        return ""
        
    for l in logs:
        m = re.compile(":.*avc.*:").search(l)
        if m:
            continue
        m = re.compile("path=\S+").search(l)
        if m:
            path = string.split(m.group(),"=").pop()                
            path = string.replace(path,"\"","")
            return path
        
        if (string.find(l,"name=")>0):
            m = re.compile("name=\S+").search(l)
            path = string.split(m.group(),"=").pop()
            path = string.replace(path,"\"","")
            if path == "(null)":
                if numPATH>1:
                    continue
                else:
                    return ""
            if numPATH==1 or inode==-1:
                return path

            ##Multiple PATH Entry
            inodeInPATH=getInode(l)
            if inodeInPATH == inode:
                return path
            
    return ""
                
def getCWDEntry(logs):
    for l in logs:
        
        if(string.find(l,"type=CWD")>=0):
            m=re.compile("cwd=\S+").search(l)
            if m:
                cwd = string.split(m.group(),"=").pop()
                #remove "
                cwd = string.replace(cwd,"\"","")
                return cwd
    return ""

def jointCWDPATH(cwd,path):

    path = cwd+"/"+path
    path = os.path.normpath(path)
    realpath = getPathWithChroot(path, inode, pid,ppid)
    if realpath=="//":
        return ""
    if realpath=="":
        return path
    return realpath
    
    

def guessPathByPATHEntry(lines,index):

    """
    First, guess full path by PATH entry
    And return guessed path
    When can not be guessed, "" is returned
    """

    line = lines[index]
    id = getAuditId(line)
    pid = getPid(line)
    ppid = getPpid(lines, index)
    inode = getInode(line)
    domain = getDomain(line)
    if(id):
        logs = getRelatedLog(lines,index)

        path =""
        cwd=""
    else:
        print "Warning no auid in line:%s" % (line)
        return ""

    path = getPATHEntry(logs,inode)

    if path=="":
        return ""

    if path[0]=="/":
        realpath = getPathWithChroot(path, inode,pid,ppid)
        if realpath =="":
            #print "Warning: inode number does not match %s" % (logs)
            #print "All candidate paths"
            #print getCandidatePathWithChroot(path,inode,pid,ppid)
            return path
        else:
            return realpath
    else:
        print "#####"+path
        #need to joint CWD
        cwd = getCWDEntry(logs)
        if cwd=="":
            print "Warning: no CWD %s"
            print logs
            return ""
        path = cwd+"/"+path
        path = os.path.normpath(path)
        realpath = getPathWithChroot(path, inode, pid,ppid)
        if realpath=="//":
            return ""
        if realpath=="":
            #print "Warning: inode number does not match %s" % (logs)
            #print "All candidate paths"
            #print getCandidatePathWithChroot(path,inode,pid,ppid)
            return path
        return realpath

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
    
def getInodeByStat(path):
    if os.path.exists(path):
        s = os.stat(path)
        return s.st_ino
    else:
        return 0

def updateInoPath(path,line):
    if path=="":
        return


    ino = getInode(line)
    secclass = getEqualValue(line,"tclass")
    if secclass == "dir": #when secclass dir,inode number is incorrect(it is for directory) in log
        ino = getInodeByStat(path)
    
    if ino:
        gInoPathDir[ino]=path
def guessPathByInoDir(line):
    ino = getInode(line)

    if ino:
        if gInoPathDir.has_key(ino):
            return gInoPathDir[ino]
                
    return ""
    
    
def guessFilePath(rule,lines,index):
    """
    guess full path information
    """
    line = lines[index]
    if rule["type"] in gExcLabelList:
        return rule["type"]

    path = guessPathByInoDir(line)
    if path=="":   
        path= guessPathByPATHEntry(lines,index)    
    
    if gCross == False:
        if path =="":
            path = guessPathByLocate(line)

        
    updateInoPath(path,line)
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
            if security=="high":
                result = appendResult(result, "c")
                result = appendResult(result, "r")
                result = appendResult(result, "s")
            else:
                result = appendResult(result, "w")
                result = appendResult(result, "r")
                result = appendResult(result, "s")
            return result
        elif rule["secclass"]=="dir" and "remove_name" in rule["permission"]:
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

"""
Example:
path:/usr/share/foo/bar 
name:foo
returns /usr/share/foo

Example:
path:/usr/foo/share/foo/bar 
name:foo
returns /usr/foo/share/foo

Error: returns None
"""
def findNameInPath(path,name):
   
    (head,tail)=os.path.split(path)

    while head!="/":
        if os.path.basename(head)==name:
            return  head
        (head,tail)=os.path.split(head)

    return None

def genFileAllow(rule,lines,index,domdoc):
    
    return __genFileAllow(rule,lines,index,domdoc)

def __genFileAllow(rule,lines,index,domdoc):
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
    line = lines[index]
    
    path = guessFilePath(rule,lines,index)

    #for lnk_file class, need special treatment to obtain real fullpath
    if rule["secclass"]=="lnk_file":
        if rule["type"]=="bin_sh_t":
            #for /bin/sh, sometimes fails to guess
            if rule["name"]=="sh":
                path ="/bin/sh"
        elif not os.path.islink(path):
            if path:
                p2 = findNameInPath(path,rule["name"])
                if p2:
                    path=p2
        elif os.path.islink(path):
            if "create" in rule["permission"]:
                ##if creating link, now we have real full path
                pass
            else:
                p = os.readlink(path)
                if rule["name"] == os.path.basename(p):
                    path = p
                else:
                    path = guessPathByLocate(line)
                    updateInoPath(path,line)
                   
    else:
        if path:
            if path[0]=="/":
                path = os.path.realpath(path)
  
            
  
    
    permList = findFilePermission(domdoc,rule,"allowfile")
    if not permList:
        permList = findFilePermission(domdoc,rule,"allowdev")
    if not permList:
        return []

    if rule["type"] == "security_t":
        return None

    spRule["ruletype"]="allowfile"
    spRule["domain"]=rule["domain"]
    spRule["type"]=rule["type"]
    spRule["name"]=rule["name"]
    spRule["secclass"]=rule["secclass"]

         
    ##make grab
    if rule["secclass"] == "dir":
        pass    
    elif os.path.islink(path):
        pass
    elif os.path.isdir(path):
        path = path + "/*"
    #convert /home -> ~/
    if re.search("^/home/", path):
        spRule["homepath"]=path #path before ~
        path = re.sub("/home/[^/]+","~",path)
        if path =="~":
            path ="~/"
        

    spRule["path"] = path
    if not os.path.isdir(path):
        permList = appendResult(permList,"r");

    spRule["permission"] = permList

    spRuleList.append(spRule)
    
    return spRuleList

def __genFileAllowCross(rule,lines,index,domdoc):
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
    line = lines[index]

    
    permList = findFilePermission(domdoc,rule,"allowfile")
    if not permList:
        permList = findFilePermission(domdoc,rule,"allowdev")
    if not permList:
        return []

    if rule["type"] == "security_t":
        return None

    spRule["ruletype"]="allowfile"
    spRule["domain"]=rule["domain"]
    spRule["type"]=rule["type"]
    spRule["path"]=rule["name"]
    if rule.has_key("path"):
        spRule["path"]=rule["path"]
    spRule["secclass"]=rule["secclass"]

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
    genRuleType=["allowpriv","allownet","allowcom","allowkey"]

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
    
def genSPDL(rule,lines,index, domdoc):
    """
    generate SPDL based on rule.
    rule is dictionary in parseLine funct    
    """

    spRuleList=[]
    line = lines[index]

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
        spRuleList= genFileAllow(rule,lines,index,domdoc)
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

def parseSyscall(line):
    result =0
    s = getEqualValue(line, "syscall")
    if s!="":
        result = string.atoi(s)

    return result


# Generate full path list from PATH= and CWD= 
# returns list of (fullpath, inode number) : inode number is integer
# If failed return ("", inode number)
# Generate full path only for existing file
def genFullPath(lines):
    inode = -1
    path = ""
    cwd = ""
    list = []
    # it is assumed that PATH,CWD appears in sequence(PATH -> CWD).
    for l in lines:

        if l.find("type=PATH") >=0:
            inode = getInode(l)
            m=re.compile("name=\S+").search(l)
            if m:
                path = string.split(m.group(),"=").pop()
                if path.find("\"") == -1: 
                    path = ""
                path = string.replace(path,"\"","")

                if path==".":
                        continue

                try:
                    os.stat(path)
                    
                    list.append((path,inode))
                except:
                    pass                
                
        
        if l.find("type=CWD")>=0 :
            m=re.compile("cwd=\S+").search(l)
            if m:
                cwd = string.split(m.group(),"=").pop()
                cwd = string.replace(cwd,"\"","")
            if path!="":
                if path[0]!="/":
                    path = cwd + "/"+path
                    path = os.path.normpath(path)
                    if path=="//":
                        list.append(("",inode))
                        continue

                    try:
                        os.stat(path)
                        list.append((path,inode))
                    except:
                        list.append(("", inode))

    return list

####
# Guess changed root after chroot, from sys_chroot and chdir logs
# and update gChrootStatus
# if lines[index] is log for chroot or syscall 12, return True
def updateChangedRoot(lines,index):
    line = lines[index]

    reg = re.compile("type=SYSCALL.*syscall=12")
   
    m = reg.search(line)
    if m:
        updateChdirInoPathDir(lines, index)
        return True
    
    reg = re.compile("avc:.*granted.*{.*sys_chroot.*}")
    m= reg.search(line)
    if not m:
        return False
      
    
    logs = getRelatedLog(lines, index)

    list = genFullPath(logs)
    path =""
    
    if list:
        (path, inode)=list[0]

        if path =="":
            if gChdirInoPathDir.has_key(inode):
                path = gChdirInoPathDir[inode]

    pid = getPid(lines[index])
    gChrootStatus[pid] = path


    return True

def updateChdirInoPathDir(lines, index):
    logs = getRelatedLog(lines, index)    
    list = genFullPath(logs)

    if list:
        (path, inode)=list[0]
        gChdirInoPathDir[inode] = path
       


def getPpidFromLine(line):
    m=re.compile("\sppid=\d+").search(line)
    if m:
        ppid = string.split(m.group(),"=").pop()
        return ppid
    return "-1"
    

def getPpid(lines, index):
    """
    get ppid from SYSCALL
    """
    auid = getUniqueAuditId(lines[index])
    if auid == None:
        return -1
    
    start = index

    i = start -1
    while i>0:
        line = lines[i]
        if auid == getUniqueAuditId(line):
           id = getPpidFromLine(line)
           if id != "-1":
               return id
        else:
            break
        i = i-1
    
    l = len(lines)    
    i = start+1
    while i < l:
        line = lines[i]
        
        if auid == getUniqueAuditId(line):
            id = getPpidFromLine(line)
            if id != "-1":
                return id
        else:
            break
        
        i = i+1

    return "-1"



###
# |lines|: whole log data
# Get logs related to log at |index|
# Related logs means, logs whose auid is the same
def getRelatedLog(lines, index):
    result = []
    result.insert(0,lines[index])
    
    start = index
    auid = getUniqueAuditId(lines[index])
    if auid == None:
        return result

    i = start -1
    while i>0:
        line = lines[i]
        if (string.find(line,"audit") != -1):          
            if auid == getUniqueAuditId(line):
                result.insert(0,line)
            else:
                break
        
        i = i-1
    
    l = len(lines)    
    i = start+1
    while i < l:
        line = lines[i]
        if (string.find(line,"audit") != -1):
            if auid == getUniqueAuditId(line):
                result.append(line)
            else:
                break
    
        i = i+1

    return result


def parseLine(lines, i):
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
    line = lines[i]
    r = updateChangedRoot(lines, i)

    if r==True:
        return None
    
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
        rule["domain"] = list[2]

    m = re.compile("tcontext=\S+").search(line)
    if m:
        list = string.split(m.group(),":")
        rule["type"] = list[2]
        
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
            str = string.replace(str," ","")            
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


'''
if do not need restorecon return ""
if need restorecon, returns restorecon command string
'''
def restoreconStr(spRule,allowFileStr):
    path = spRule["path"]
    if spRule.has_key("homepath"):
        path = spRule["homepath"]
    
    if spRule["secclass"]=="dir":
        return "" # for secclass=dir, matchpathcon(path) and type does not match
    if path =="":
        return ""
    if path[0]!='/':
        return ""

    path = re.sub("\*","",path)
    
    command = gMatchpathcon + " " +path
    input=os.popen(command, "r")
    lines = input.readlines()
    if input.close():
        return ""
    

    line  = lines[0].strip("\n")
    type = line.split(':')[2]
    
    type = re.sub("^dir_","",type)
    logType = spRule["type"]
    

    logType = re.sub("^dir_","",logType)

    if type == logType:
        return ""

    if os.path.realpath(path)!=path:
        return ""

    #check hardlink
    if not os.path.isdir(path):
        if os.path.exists(path):
            if os.path.islink(path):
                return ""

            s = os.stat(path)
            if s.st_nlink > 1:
                result = _("%s is hardlinked.\n #Nothing generated for safety.\n") % (path)
                result = result +"#"+allowFileStr
                return result

   
                
    result = "restorecon -R "+path
    return result
 


def allowfileStr(spRule):
    str=""

    if spRule["path"]=="":
        str = "allow "+spRule["name"]+" "
    else:
        str="allow "+spRule["path"]+" "

    if os.path.isdir(spRule["path"]):
        if spRule["secclass"]=="dir" and "w" in spRule["permission"]:
            if  gHighSecurityFlag == False:
                str="allow "+spRule["path"]+"/* "
        
    
    permList=spRule["permission"]
    if "dummy" in permList:
        str = _("#allow:Nothing generated for safety\n")
        return str
    
    str = str+" "+permListToStr(permList)+";"
    
    path = spRule["path"]
    if path =="":
        str = "#"+str
        str = _("#Failed to generate, because failed to obtain fullpath.\n") +str

    if gRestoreconFlag:
        restorecon = restoreconStr(spRule,str)
        if restorecon != "":
            str = "#" + restorecon
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

def allowkeyStr(spRule,security="low"):
    str =""
    option = spRule["option"]

    str ="allowkey "+domainToRole(spRule["type"])+" "+option+" ;"
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
            if spRule["type"] in ("unpriv_tcp_port_t", "unpriv_udp_port_t"):
                port = "1024-"

    if suboption =="server":
        port =src
        if string.atoi(port) > 10000:
            if spRule["type"] in ("unpriv_tcp_port_t", "unpriv_udp_port_t"):
                port = "1024-"

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
        if spRule["domain"]=="unlabeled_t":
            print "#Warning Broken domain, skipped."
            continue
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
        elif ruletype =="allowkey":
            ruleStr = allowkeyStr(spRule)
            
        outStruct.append((fileName,line,ruleStr))
      
    return outStruct

############
#####Main function

gFileClass = ["dir","file","lnk_file","sock_file", "fifo_file","chr_file","blk_file" ]

#Path to simplified policy
#
#labels defined by allow exclusive rule
gExcLabelList=getExcLabelList(gGeneratedPolicy)


#labels used for allowfs rule
gFsLabelList=getFsLabelList(gConverterConf)
#list of domain defined in SPDL
#Note that suffix of gRoleList is "_t" not "_r"
( gDomainList, gRoleList ) = getDomainList(gAllsp)

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

#if True, generates restorecon command
gRestoreconFlag = False

gOutput="/etc/selinux/seedit/src/simplified_policy"

