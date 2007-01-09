prefix ?= $(DESTDIR)/usr
sysconfdir ?= $(DESTDIR)/etc
SRC = seedit-gui-domain-manager.py seedit-gui-role-manager.py seedit-gui-edit.py seedit-gui-generate-policy.py seedit-gui-status.py seedit-gui.py seedit/ui/GUICommon.py seedit/ui/UILogic.py
PYTHON_VER ?= 2.4
DISTRO ?= fc6
PAM_INCLUDE_SUPPORT ?= y

all:

install: 
	mkdir -p $(prefix)/share/icons/seedit
	install -m 644 ./icons/*  $(prefix)/share/icons/seedit
	mkdir -p $(prefix)/lib/python$(PYTHON_VER)/site-packages/seedit/ui
	install -m 755 seedit/ui/*	$(prefix)/lib/python$(PYTHON_VER)/site-packages/seedit/ui
	mkdir -p $(prefix)/sbin
	install -m 755 seedit-gui.py $(prefix)/sbin/seedit-gui
	install -m 755 seedit-gui-status.py $(prefix)/sbin/seedit-gui-status

	install -m 755 seedit-gui-domain-manager.py $(prefix)/sbin/seedit-gui-domain-manager
	install -m 755 seedit-gui-role-manager.py $(prefix)/sbin/seedit-gui-role-manager
	install -m 755 seedit-gui-generate-policy.py $(prefix)/sbin/seedit-gui-generate-policy
	install -m 755 seedit-gui-load.py $(prefix)/sbin/seedit-gui-load

	install -m 755 seedit-gui-edit.py $(prefix)/sbin/seedit-gui-edit
	mkdir -p $(prefix)/share/locale/ja/LC_MESSAGES/
	install -m 644 po/ja.mo $(prefix)/share/locale/ja/LC_MESSAGES/seedit.mo

	mkdir -p $(prefix)/bin
	ln -sf   consolehelper  $(prefix)/bin/seedit-gui
	mkdir -p $(sysconfdir)/security/console.apps
	install -m 644 console.apps/seedit-gui $(sysconfdir)/security/console.apps
	mkdir -p $(sysconfdir)/pam.d
	if [ $(PAM_INCLUDE_SUPPORT) = "y" ];then\
		install -m 644 pam.d/seedit-gui.include   $(sysconfdir)/pam.d/seedit-gui;\
	else \
		install -m 644 pam.d/seedit-gui.noinclude   $(sysconfdir)/pam.d/seedit-gui;\
	fi
clean:


pot:
	pygettext.py $(SRC)
mo:
	msgfmt.py po/ja.po
