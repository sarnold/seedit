# $Id: Makefile,v 1.8 2006/05/05 16:05:36 ynakam Exp $

#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

SELINUXTYPE=seedit
sysconfdir = $(DESTDIR)/etc
prefix = $(DESTDIR)/usr
DISTRO = COS4
MODULAR=n
CONVERTER=/usr/local/bin/seedit-converter
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

policy:  
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

install: policy dir
	mkdir -p $(prefix)/share/seedit/scripts
	install -m 755 seedit-installhelper.sh $(prefix)/share/seedit/scripts
	cp -r policy/simplified_policy/*  $(SEEDITCONFROOT)/policy
	cp src/setrans.conf	$(POLICYROOT)
	mkdir -p $(prefix)/share/seedit/sepolicy
	if [ $(MODULAR) = "y" ];then \
		cp policy/sepolicy/base.pp  $(prefix)/share/seedit/sepolicy;\
	fi
	if [ $(MODULAR) = "n" ];then \
		cp policy/sepolicy/policy.*  $(prefix)/share/seedit/sepolicy;\
	fi

	cp policy/sepolicy/unconfined_domains  $(prefix)/share/seedit/sepolicy
	cp policy/sepolicy/confined_domains  $(prefix)/share/seedit/sepolicy

	if [ -e $(POLICYROOT)/contexts/files/file_contexts ]; then \
		cp $(POLICYROOT)/contexts/files/file_contexts $(POLICYROOT)/contexts/files/file_contexts.old;\
	fi
	cd policy;make install DESTDIR=$(DESTDIR)
	if [ -e $(DYNAMIC_CONTEXTS) ] ; then cat $(DYNAMIC_CONTEXTS) >> policy/sepolicy/file_contexts; fi
	cp policy/sepolicy/file_contexts  $(POLICYROOT)/contexts/files/file_contexts

	if [ ! -e $(POLICYROOT)/contexts/files/file_contexts.old ]; then \
		cp $(POLICYROOT)/contexts/files/file_contexts $(POLICYROOT)/contexts/files/file_contexts.old;\
	fi
	rm $(SEEDITCONFROOT)/policy/all.sp
	touch $(POLICYROOT)/users/system.users
	touch $(POLICYROOT)/users/local.users


postconfig: install
	cat $(SELINUXCONF) |sed -e 's/^SELINUX=.*$$/SELINUX=permissive/'|sed -e 's/^SELINUXTYPE=.*$$/SELINUXTYPE=$(SELINUXTYPE)/' >$(SELINUXCONF).tmp
	mv $(SELINUXCONF) $(SELINUXCONF).orig
	mv $(SELINUXCONF).tmp $(SELINUXCONF)
	touch /.autorelabel
	$(RESTORECON) $(SELINUXCONF)


clean:
	rm -rf policy doc/*.aux doc/*.toc doc/*.pdf src/base_policy/unsupported.te src/macros/seedit_macros.te

