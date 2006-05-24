
CC		= gcc
CFLAGS		= -Wall -O2 -g -DDEBUG=1 -DDIRSEARCH=1
LD		= -ll -lselinux 
INCLUDE		= -I/usr/include/selinux -I/usr/include/libxml2/ -I../include
LDPATH		= -L/usr/lib
CONVERTEROBJS	=  action.o  file_label.o convert.o security_class.o initial_policy.o out_file_acl.o seedit-converter.o hashtab.o preprocess_include.o
LIBSEEDIT = ../lib/libseedit.a

prefix = /usr
INSTALL_PATH	= $(prefix)

all: seedit-converter

seedit-converter: $(CONVERTEROBJS) $(LIBSEEDIT)
	$(CC) -o $@ $(CONVERTEROBJS) $(LIBSEEDIT) $(LD) $(LDPATH)

.c.o:
	$(CC) -c $(CFLAGS) $(INCLUDE) $<


action.o: action.h hashtab.h file_label.h global.h initial_policy.h
seedit-converter.o:action.h initial_policy.h  security_class.h

hashtab.o: hashtab.h

file_label.o: hashtab.h file_label.h global.h 

convert.o: file_label.h action.h hashtab.h convert.h  out_file_acl.h initial_policy.h security_class.h global.h

out_file_acl.o: global.h hashtab.h action.h

initial_policy.o: initial_policy.h security_class.h  file_label.h global.h

security_class.o:  security_class.h initial_policy.h

preprocess_include.o: preprocess_include.h

action.h: global.h

install: seedit-converter
	mkdir -p $(INSTALL_PATH)
	mkdir -p $(INSTALL_PATH)/bin
	install -m 755 seedit-converter $(INSTALL_PATH)/bin

uninstall:
	rm  $(INSTALL_PATH)/bin/seedit-converter

clean:
	rm -f *.o seedit-converter lex.yy.c y.tab.c a.out 
