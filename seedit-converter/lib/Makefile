
CC		= gcc
LEX		= lex
YACC		= yacc
CFLAGS		= -Wall -O2 -g -DDEBUG=1
INCLUDE = -I../include 
OBJS 	= y.tab.o lex.yy.o parse.o common.o
TARGET = libseedit.a
prefix = /usr
PYTHONVER = 2.4
PYTHONROOT = $(prefix)/lib/python$(PYTHONVER)/site-packages
all: $(TARGET)

$(TARGET):  $(OBJS)
	$(AR) rcs $@ $^
	ranlib $@
.c.o:
	$(CC) -c $(CFLAGS) $(INCLUDE) $<

y.tab.o: y.tab.c
	$(CC) -c $(CFLAGS) y.tab.c -I../include 

lex.yy.c: middle_lang.l
	$(LEX) middle_lang.l 

y.tab.c: middle_lang.y
	$(YACC) -d  middle_lang.y

#install only python lib
install:
	mkdir -p $(PYTHONROOT)/seedit
	cp -r ./python/seedit $(PYTHONROOT)
uninstall:
	rm -rf $(PYTHONROOT)/seedit

clean:
	rm -f $(OBJS) y.tab.c lex.yy.c y.tab.h $(TARGET)
