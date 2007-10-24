prefix ?= $(DESTDIR)/usr
sysconfdir ?= $(DESTDIR)/etc
SRC = seedit-gui-domain-manager.py seedit-gui-role-manager.py seedit-gui-edit.py seedit-gui-generate-policy.py seedit-gui-status.py seedit-gui.py seedit/ui/GUICommon.py seedit/ui/UILogic.py
DISTRO ?= fc6
PAM_INCLUDE_SUPPORT ?= y
PYTHON_SITELIB ?=  $(prefix)/lib/python2.4/site-packages/

all:

install: 
	mkdir -p $(prefix)/share/icons/seedit
	install -p -m 644 ./icons/*  $(prefix)/share/icons/seedit
	mkdir -p $(PYTHON_SITELIB)/seedit/ui
	install -p -m 755 seedit/ui/*  $(PYTHON_SITELIB)/seedit/ui
	mkdir -p $(prefix)/sbin
	install -p -m 755 seedit-gui.py $(prefix)/sbin/seedit-gui
	install -p -m 755 seedit-gui-status.py $(prefix)/sbin/seedit-gui-status

	install -p -m 755 seedit-gui-domain-manager.py $(prefix)/sbin/seedit-gui-domain-manager
	install -p -m 755 seedit-gui-role-manager.py $(prefix)/sbin/seedit-gui-role-manager
	install -p -m 755 seedit-gui-generate-policy.py $(prefix)/sbin/seedit-gui-generate-policy
	install -p -m 755 seedit-gui-load.py $(prefix)/sbin/seedit-gui-load

	install -p -m 755 seedit-gui-edit.py $(prefix)/sbin/seedit-gui-edit
	mkdir -p $(prefix)/share/locale/ja/LC_MESSAGES/
	install -p -m 644 po/ja.mo $(prefix)/share/locale/ja/LC_MESSAGES/seedit.mo

	mkdir -p $(prefix)/bin
	ln -sf   consolehelper  $(prefix)/bin/seedit-gui
	mkdir -p $(sysconfdir)/security/console.apps
	install -p -m 644 console.apps/seedit-gui $(sysconfdir)/security/console.apps
	mkdir -p $(sysconfdir)/pam.d
	if [ $(PAM_INCLUDE_SUPPORT) = "y" ];then\
		install -p -m 644 pam.d/seedit-gui.include   $(sysconfdir)/pam.d/seedit-gui;\
	else \
		install -p -m 644 pam.d/seedit-gui.noinclude   $(sysconfdir)/pam.d/seedit-gui;\
	fi

cross-install: 	
	mkdir -p $(DESTDIR)
	cp -r ./icons	$(DESTDIR)
	mkdir -p $(DESTDIR)/seedit/ui
	install -p -m 755 seedit/ui/*  $(DESTDIR)/seedit/ui
	install -p -m 755 seedit-gui.py $(DESTDIR)/seedit-gui
	install -p -m 755 seedit-gui-domain-manager.py $(DESTDIR)/seedit-gui-domain-manager
	install -p -m 755 seedit-gui-generate-policy.py $(DESTDIR)/seedit-gui-generate-policy
	install -p -m 755 seedit-gui-load.py $(DESTDIR)/seedit-gui-load
	install -p -m 755 seedit-gui-edit.py $(DESTDIR)/seedit-gui-edit

clean:


pot:
	pygettext.py $(SRC)
mo:
	msgfmt.py po/ja.po
