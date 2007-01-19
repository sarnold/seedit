
CC		= gcc
LEX		= lex
YACC		= yacc
CFLAGS		?= -Wall -O2 -g -DDEBUG=1
INCLUDE = -I../include  -I/usr/include/selinux
OBJS 	= y.tab.o lex.yy.o parse.o common.o
TARGET = libseedit.a
prefix ?= /usr
PYTHON_SITELIB ?=  $(prefix)/lib/python2.4/site-packages/
PYTHON_MODULE_ROOT = $(PYTHON_SITELIB)

all: $(TARGET)

$(TARGET):  $(OBJS)
	$(AR) rcs $@ $^
	ranlib $@
.c.o:
	$(CC) -c $(CFLAGS) $(INCLUDE) $<

y.tab.o: y.tab.c
	$(CC) -c $(CFLAGS) y.tab.c -I../include -I/usr/include/selinux

lex.yy.c: middle_lang.l
	$(LEX) middle_lang.l 

y.tab.c: middle_lang.y
	$(YACC) -d  middle_lang.y

#install only python lib
install:
	mkdir -p $(PYTHON_MODULE_ROOT)/seedit
	install -m 755  ./python/seedit/*.py $(PYTHON_MODULE_ROOT)/seedit
uninstall:
	rm -rf $(PYTHON_MODULE_ROOT)/seedit

clean:
	rm -f $(OBJS) y.tab.c lex.yy.c y.tab.h $(TARGET)
