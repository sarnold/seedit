#!/usr/bin/python

import string
import sys


def strXML(str):
    """
    """

    list = string.split(str, ":")

    list2 = string.split(list[0])

    domain = list2[1]
    type=list2[2]

    if domain=="$1":
        domain="domain"

    if type=="$2":
        type ="type"

    print "<rule value=\"allow\">"
    print "<domain value=\"%s\"/>" % domain

    print "<type value=\"%s\"/>" % type

    list3=string.split(list[1])

    obj=list3[0]

    print "<secclass value=\"%s\"/>" % obj

    permlist=list3[1:]
    for perm in permlist:
        perm = string.replace(perm, ";", "")
        if(perm == "{"  or perm=="}" ):
            continue
        print "<permission value=\"%s\"/>" % perm

    print "</rule>"

###main"
strList=[]

str="allow $1 $2:dir { read getattr lock search ioctl add_name remove_name write };"



str="allow $1 port_type:tcp_socket name_connect;"
strList.append(str)
str="allow $1 self:tcp_socket connect;"
strList.append(str)
str="allow $1 self:tcp_socket connect;"
strList.append(str)

for str in strList:
    strXML(str)
