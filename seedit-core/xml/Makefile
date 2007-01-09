
CC		= gcc
CFLAGS		= -Wall -O2 -g -DDEBUG=1 -DDIRSEARCH=1
LD		= -ll -lselinux
INCLUDE		= -I/usr/include/selinux -I/usr/include/libxml2/ -I../include
LDPATH		= -L/usr/lib
OBJS	=  seedit-spdl2xml.o
LIBSEEDIT = ../lib/libseedit.a

prefix = /usr
INSTALL_PATH	= $(prefix)

all:seedit-spdl2xml

seedit-spdl2xml: $(OBJS)
	$(CC) -o $@ $(OBJS) $(LIBSEEDIT) $(LD) -lxml2 $(LDPATH)

.c.o:
	$(CC) -c $(CFLAGS) $(INCLUDE) $<

install: seedit-spdl2xml seedit-xml2spdl.py
	mkdir -p $(INSTALL_PATH)
	mkdir -p $(INSTALL_PATH)/bin
	install -m 755 seedit-spdl2xml $(INSTALL_PATH)/bin/
	install -m 755 seedit-xml2spdl.py $(INSTALL_PATH)/bin/seedit-xml2spdl

uninstall: 
	rm  $(INSTALL_PATH)/bin/seedit-spdl2xml
	rm  $(INSTALL_PATH)/bin/seedit-xml2spdl

clean:
	rm -f *.o seedit-export  
