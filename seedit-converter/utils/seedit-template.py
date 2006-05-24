#!/usr/bin/python
# Author: Yuichi Nakamura <ynakam@gwu.edu>
# Copyright (c) 2005 Yuichi Nakamura
# License: GPL

"""
Generates policy frame
"""
import getopt
import sys
import os

def printUsage():
    print ("usage:%s -d <domain> -e <executable> -o <output>" % sys.argv[0])
    sys.exit(1)


############Main func
domain=""
exe =""
output=sys.stdout

try:
    opts, args = getopt.getopt(sys.argv[1:], "d:e:o:", ["domain=","entrypoint=","output="])
except getopt.GetoptError:
    printUsage()



for opt,arg in opts:
    if opt in ("-d", "--domain"):
        domain = arg
    if opt in ("-e", "--entrypoint"):
        exe = arg
    if opt in ("-o", "--output"):
        filename = arg
        try:
            output = open(filename, 'w')
        except:
            print "Output file open error %s" % filename
            sys.exit(1)

if domain=="" or exe =="":
    printUsage()


exe = os.path.realpath(exe)

output.write("{\n")
output.write("domain %s;\n" % domain)
output.write("program %s;\n" % exe)
output.write("include common-relaxed.sp;\n")
output.write("include daemon.sp;\n")
output.write("include nameservice.sp;\n\n")
output.write("}\n")
