prefix = /usr


all:

install:
	mkdir -p $(prefix)/share/icons/seedit
	install -m 744 ./icons/*  $(prefix)/share/icons/seedit
	mkdir -p $(prefix)/lib/seedit
	install -m 744 seedit/*	$(prefix)/lib/seedit
	install -m 744 seedit-gui.py $(prefix)/sbin/seedit-gui
	install -m 744 seedit-gui-status.py $(prefix)/sbin/
	install -m 744 seedit-gui-domain-manager.py $(prefix)/sbin/
	install -m 744 seedit-gui-generate-policy.py $(prefix)/sbin/

clean:
