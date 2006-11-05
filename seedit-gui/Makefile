prefix = /usr
sysconfdir = /etc
SRC = seedit-gui-domain-manager.py seedit-gui-role-manager.py seedit-gui-edit.py seedit-gui-generate-policy.py seedit-gui-status.py seedit-gui.py seedit/ui/GUICommon.py seedit/ui/UILogic.py
PYTHON_VER=2.4


all:

install: 
	mkdir -p $(prefix)/share/icons/seedit
	install -m 644 ./icons/*  $(prefix)/share/icons/seedit
	mkdir -p $(prefix)/lib/python$(PYTHON_VER)/site-packages/seedit/ui
	install -m 744 seedit/ui/*	$(prefix)/lib/python$(PYTHON_VER)/site-packages/seedit/ui
	mkdir -p $(prefix)/sbin
	install -m 744 seedit-gui.py $(prefix)/sbin/seedit-gui
	install -m 744 seedit-gui-status.py $(prefix)/sbin/seedit-gui-status

	install -m 744 seedit-gui-domain-manager.py $(prefix)/sbin/seedit-gui-domain-manager
	install -m 744 seedit-gui-role-manager.py $(prefix)/sbin/seedit-gui-role-manager
	install -m 744 seedit-gui-generate-policy.py $(prefix)/sbin/seedit-gui-generate-policy
	install -m 744 seedit-gui-load.py $(prefix)/sbin/seedit-gui-load

	install -m 744 seedit-gui-edit.py $(prefix)/sbin/seedit-gui-edit
	mkdir -p $(prefix)/share/locale/ja/LC_MESSAGES/
	install -m 644 po/ja.mo $(prefix)/share/locale/ja/LC_MESSAGES/seedit-gui.mo

	mkdir -p $(prefix)/bin
	ln -sf /usr/bin/consolehelper  $(prefix)/bin/seedit-gui
	mkdir -p $(sysconfdir)/security/console.apps
	install -m 644 console.apps/seedit-gui $(sysconfdir)/security/console.apps
	mkdir -p $(prefix)/share/applications/
	install -m 644 desktop/seedit-gui.desktop $(prefix)/share/applications
	mkdir -p $(prefix)/share/pixmaps/
	install -m 644 icons/seedit-gui.png $(prefix)/share/pixmaps


clean:


pot:
	pygettext.py $(SRC)
mo:
	msgfmt.py po/ja.po
