CC		= gcc
CFLAGS		?= -Wall -O2 -g -DDEBUG=1
LD		= -lfl -lselinux 
INCLUDE		= -I../include
LDPATH		?= -L/usr/lib
CONVERTEROBJS	=  action.o  file_label.o convert.o security_class.o initial_policy.o out_file_acl.o seedit-converter.o hashtab.o preprocess_include.o out_macro.o
LIBSEEDIT = ../lib/libseedit.a
prefix ?= /usr
INSTALL_PATH	= $(prefix)
INCLUDEDIR ?= $(prefix)/include
override CFLAGS += -I../include -I$(INCLUDEDIR)

all: seedit-converter

seedit-converter: $(CONVERTEROBJS) $(LIBSEEDIT)
	$(CC) -o $@ $(CONVERTEROBJS) $(LIBSEEDIT) $(LD) $(LDPATH)

.c.o:
	$(CC) -c $(CFLAGS) $(INCLUDE) $<


action.o: action.h hashtab.h file_label.h global.h initial_policy.h
seedit-converter.o:action.h initial_policy.h  security_class.h out_macro.h

hashtab.o: hashtab.h

file_label.o: hashtab.h file_label.h global.h  action.h

convert.o: file_label.h action.h hashtab.h convert.h  out_file_acl.h initial_policy.h security_class.h global.h out_macro.h

out_file_acl.o: global.h hashtab.h action.h out_macro.h
out_macro.o: global.h hashtab.h out_macro.h

initial_policy.o: initial_policy.h security_class.h  file_label.h global.h

security_class.o:  security_class.h initial_policy.h

preprocess_include.o: preprocess_include.h

action.h: global.h

install: seedit-converter
	mkdir -p $(INSTALL_PATH)
	mkdir -p $(INSTALL_PATH)/bin
	install -p -m 755 seedit-converter $(INSTALL_PATH)/bin

uninstall:
	rm  $(INSTALL_PATH)/bin/seedit-converter

clean:
	rm -f *.o seedit-converter lex.yy.c y.tab.c a.out 

test: all
	mkdir -p sepolicy
	./seedit-converter -p -i ./simplified_policy/all.sp -o ./sepolicy -b /usr/share/seedit/base_policy -I ./simplified_policy/include
	./seedit-converter -t 1 -i ./simplified_policy/all.sp -o ./sepolicy -b /usr/share/seedit/base_policy -I ./simplified_policy/include --profile-data ./sepolicy/profile.data --busybox
	m4  -Imacros -s ./macros/*.te ./sepolicy/generated.conf > ./sepolicy/policy.conf;
	m4  -Imacros -s ./macros/mcs_macros.te ./sepolicy/file_contexts.m4 >./sepolicy/file_contexts;
	checkpolicy -o sepolicy/policy.21 -c 21 ./sepolicy/policy.conf
