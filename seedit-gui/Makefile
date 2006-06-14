prefix = /usr

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
	mkdir -p $(prefix)/share/locale/ja/LC_MESSAGES/
	install -m 744 po/ja.mo $(prefix)/share/locale/ja/LC_MESSAGES/seedit-gui.mo

clean:


pot:
	pygettext.py $(SRC)
mo:
	msgfmt.py po/ja.po
