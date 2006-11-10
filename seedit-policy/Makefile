# $Id: Makefile,v 1.8 2006/05/05 16:05:36 ynakam Exp $

#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

SELINUXTYPE=seedit
sysconfdir = $(DESTDIR)/etc
prefix = $(DESTDIR)/usr
DISTRO = COS4
MODULAR=n
CONVERTER=/usr/bin/seedit-converter
LOADPOLICY=/usr/sbin/load_policy
SEMODULE_PACKAGE=/usr/bin/semodule_package
CHECKPOLICY=/usr/bin/checkpolicy
FIXFILES=/sbin/fixfiles
RESTORECON=/sbin/restorecon
SELINUXCONF=$(sysconfdir)/selinux/config
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
	mkdir -p $(POLICYROOT)/contexts/files
	mkdir -p $(POLICYROOT)/contexts/users
	mkdir -p $(SEEDITCONFROOT)/policy

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

install: dir
	mkdir -p $(prefix)/share/seedit/scripts
	install -m 755 seedit-installhelper.sh $(prefix)/share/seedit/scripts
	cp -r policy/simplified_policy/*  $(SEEDITCONFROOT)/policy
	cp src/setrans.conf	$(POLICYROOT)
	echo "#" >  $(POLICYROOT)/users/system.users
	echo "#" >  $(POLICYROOT)/users/local.users
	mkdir -p $(prefix)/share/seedit/sepolicy
	if [ -e $(DYNAMIC_CONTEXTS) ] ; then \
		cp $(DYNAMIC_CONTEXTS)  $(prefix)/share/seedit/sepolicy/base_policy/contexts;\
	else \
		echo "#" > $(prefix)/share/seedit/sepolicy/base_policy/contexts/dynamic_contexts;\
	fi

clean:
	rm -rf policy doc/*.aux doc/*.toc doc/*.pdf src/base_policy/unsupported.te src/macros/seedit_macros.te

