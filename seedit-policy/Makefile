# $Id: Makefile,v 1.8 2006/05/05 16:05:36 ynakam Exp $

#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

SELINUXTYPE=seedit
sysconfdir = $(DESTDIR)/etc
prefix ?= $(DESTDIR)/usr
DISTRO ?= fc6
MODULAR ?= y
AUDITRULES ?= /etc/audit/audit.rules

CONVERTER=/usr/bin/seedit-converter
LOADPOLICY=/usr/sbin/load_policy
SEMODULE_PACKAGE=/usr/bin/semodule_package
CHECKPOLICY=/usr/bin/checkpolicy
FIXFILES=/sbin/fixfiles
RESTORECON=/sbin/restorecon
SELINUXCONF=/etc/selinux/config
POLICYROOT=$(sysconfdir)/selinux/$(SELINUXTYPE)
SEEDITCONFROOT=$(sysconfdir)/seedit
CONFDIR=./policy/simplified_policy
BASEPOLICYDIR=./policy/base_policy
MACRODIR=./policy/macros
OUTDIR =./policy/sepolicy
DYNAMIC_CONTEXTS=./distro/$(DISTRO)/dynamic_contexts
SPDLSPEC=./src/base_policy/spdl_spec.xml

dir:
	mkdir -p $(POLICYROOT)/policy
	mkdir -p $(POLICYROOT)/users/
	mkdir -p $(POLICYROOT)/contexts/files
	mkdir -p $(POLICYROOT)/contexts/users
	mkdir -p $(SEEDITCONFROOT)

installhelper-include:
	echo "#! /bin/sh" > seedit-installhelper-include.sh
	echo "export SELINUXCONF=$(SELINUXCONF)" >> seedit-installhelper-include.sh
	echo "export AUDITRULES=$(AUDITRULES)" >> seedit-installhelper-include.sh
	echo "export MODULAR=$(MODULAR)" >> seedit-installhelper-include.sh

install: dir installhelper-include
	mkdir -p $(prefix)/share/seedit/scripts
	install -m 755 seedit-installhelper.sh $(prefix)/share/seedit/scripts
	install -m 755 seedit-installhelper-include.sh $(prefix)/share/seedit/scripts

	if [ -e src/simplified_policy.$(DISTRO) ];then \
		cp  -r src/simplified_policy.$(DISTRO)  $(SEEDITCONFROOT)/policy;\
	else \
		cp  -r src/simplified_policy  $(SEEDITCONFROOT)/policy;\
	fi

	cp src/setrans.conf	$(POLICYROOT)
	mkdir -p $(prefix)/sbin
	install -m 755 seedit-init.sh $(prefix)/sbin/seedit-init

convert_test:  
	mkdir -p policy
	if [ -e src/simplified_policy.$(DISTRO) ];then \
		cp -r src/simplified_policy.$(DISTRO) policy/simplified_policy;\
	else \
		cp -r src/simplified_policy policy/simplified_policy;\
	fi

	cp -r /usr/share/seedit//base_policy policy/
	cp -r /usr/share/seedit/macros policy/
	cp /usr/share/seedit/Makefile policy/Makefile;\

	cd policy ;make 
	if [ -e $(DYNAMIC_CONTEXTS) ] ; then cat $(DYNAMIC_CONTEXTS) >> policy/sepolicy/file_contexts; fi
	if [ $(MODULAR) = "y" ]; then \
		$(SEMODULE_PACKAGE) -s $(BASEPOLICYDIR)/seusers -m policy/sepolicy/base.mod -f policy/sepolicy/file_contexts -o policy/sepolicy/base.pp;\
	fi
	if [ -e $(DYNAMIC_CONTEXTS) ] ; then cat $(DYNAMIC_CONTEXTS) >> policy/sepolicy/file_contexts; fi

clean:
	rm -rf policy

