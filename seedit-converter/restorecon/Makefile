#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

# Installation directories.
prefix = /usr
DISTRO = FC5
CFLAGS ?= -Werror -Wall -W
override CFLAGS += -I$(prefix)/include -D_FILE_OFFSET_BITS=64 -D_GNU_SOURCE -I../include -D$(DISTRO)
LDLIBS += -lselinux  -L$(prefix)/lib
LIBSEEDIT = ../lib/libseedit.a

all: seedit-restorecon

seedit-restorecon:  seedit-restorecon.o is_customizable_type.o
	$(CC) $(LDFLAGS) -o seedit-restorecon seedit-restorecon.o is_customizable_type.o $(LIBSEEDIT) $(LDLIBS) 




install: all
	install -m 755 seedit-restorecon $(prefix)/sbin 


clean:
	-rm -f seedit-restorecon *.o 
