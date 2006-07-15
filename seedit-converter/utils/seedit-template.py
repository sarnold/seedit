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
Generates policy frame
"""
import getopt
import sys
import os
import re

def printUsage():
    print ("usage:\n For domain: %s -d <domain> -e <executable> -o <output directory>" % sys.argv[0])
    print ("\tFor role: %s -d <role> -e <user> -o <output directory>" % sys.argv[0])
    print ("\t-n option skipps seedit-load")
    
    sys.exit(1)

def outDomain(output, domain, exe):
    exe = os.path.realpath(exe)
    output.write("{\n")
    output.write("domain %s;\n" % domain)
    output.write("program %s;\n" % exe)
    output.write("include common-relaxed.sp;\n")
    output.write("include daemon.sp;\n")
    output.write("include nameservice.sp;\n\n")
    output.write("}\n")


def outRole(output, role, user):

    output.write("{\n")
    output.write("role %s;\n" % role)
    output.write("user %s;\n" % user)
    output.write("include user_common.sp;\n")
    output.write("include common-relaxed.sp;\n")
    output.write("allow ~/** r,w,s;\n")
    output.write("allowpriv part_relabel;\n")
    output.write("allowpriv dac_override;\n")
    output.write("allowpriv dac_read_search;\n")    
    output.write("}\n")


############Main func
domain=""
role=""
exe =""
user =""
output=sys.stdout
outdir =""
filename =""


try:
    opts, args = getopt.getopt(sys.argv[1:], "r:d:e:o:u:", ["role=","domain=","entrypoint=","output=","user="])
except getopt.GetoptError:
    printUsage()



for opt,arg in opts:
    if opt in ("-r","--role"):
        role = arg
        if not re.search("_r$", role):
            print "Role must end with _r"            
            sys.exit(1)
    if opt in ("-d", "--domain"):
        domain = arg
        if not re.search("_t$", domain):
            print "Domain must end with _t"            
            sys.exit(1)

        
    if opt in ("-e", "--entrypoint"):
        exe = arg
    if opt in ("-o", "--output"):
        outdir = arg
    if opt in ("-u", "--user"):
        user = arg
    



if (domain=="" and role==""):
    printUsage()


if outdir!= "":
    if domain != "":
        filename = outdir+"/"+domain+".sp"
    if role != "":
        filename = outdir+"/"+role+".sp"

    try:
        output = open(filename, 'w+')
    except:
        print "Output file open error %s" % filename
        sys.exit(1)


if domain !="":
    outDomain(output, domain, exe)

elif role  !="":
    outRole(output, role, user)


if filename!="":    
    output.seek(0)
    print "Following is outputted in file: %s" % filename
    lines = output.readlines()
    for line in lines:
        sys.stdout.write(line)
