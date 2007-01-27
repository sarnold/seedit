
prefix ?= /usr
INSTALL_PATH	= $(prefix)

all:

clean:

install: audit2spdl.py seedit-load.py seedit-unconfined.py seedit-template.py
	mkdir -p $(INSTALL_PATH)
	mkdir -p $(INSTALL_PATH)/bin
	mkdir -p $(INSTALL_PATH)/sbin
	install -p -m 755 audit2spdl.py $(INSTALL_PATH)/bin/audit2spdl
	install -p -m 755 seedit-load.py $(INSTALL_PATH)/sbin/seedit-load
	install -p -m 755 seedit-rbac.sh $(INSTALL_PATH)/sbin/seedit-rbac
	install -p -m 755 seedit-unconfined.py $(INSTALL_PATH)/bin/seedit-unconfined
	install -p -m 755 seedit-template.py $(INSTALL_PATH)/bin/seedit-template
uninstall:
	rm $(INSTALL_PATH)/bin/audit2spdl
