prefix = /usr
sysconfdir = /etc
SRC = seedit-gui-domain-manager.py seedit-gui-edit.py seedit-gui-generate-policy.py seedit-gui-status.py seedit-gui.py seedit/ui/GUICommon.py seedit/ui/UILogic.py



all:

install:
	mkdir -p $(prefix)/share/icons/seedit
	install -m 744 ./icons/*  $(prefix)/share/icons/seedit
	mkdir -p $(prefix)/lib/seedit/ui
	install -m 744 seedit/ui/*	$(prefix)/lib/seedit/ui
	mkdir -p $(prefix)/sbin
	install -m 744 seedit-gui.py $(prefix)/sbin/seedit-gui
	install -m 744 seedit-gui-status.py $(prefix)/sbin/seedit-gui-status
	install -m 744 seedit-gui-domain-manager.py $(prefix)/sbin/seedit-gui-domain-manager
	install -m 744 seedit-gui-generate-policy.py $(prefix)/sbin/seedit-gui-generate-policy
	install -m 744 seedit-gui-edit.py $(prefix)/sbin/seedit-gui-edit
	mkdir -p $(prefix)/share/locale/ja/LC_MESSAGES/
	install -m 744 po/ja.mo $(prefix)/share/locale/ja/LC_MESSAGES/seedit-gui.mo

	ln -s $(prefix)/bin/consolehelper  /usr/bin/seedit-gui
	mkdir -p $(sysconfdir)/security
	install -m 744 security/seedit-gui $(sysconfdir)/security
	mkdir -p $(sysconfdir)/pam.d
	install -m 744 pam.d/seedit-gui    $(sysconfdir)/pam.d
	mkdir -p $(prefix)/share/applications/
	install -m 744 desktop/seedit-gui.desktop $(prefix)/share/applications


clean:


pot:
	pygettext.py $(SRC)
mo:
	msgfmt.py po/ja.po
