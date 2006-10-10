# $Id: Makefile,v 1.8 2006/05/05 16:05:36 ynakam Exp $

#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

SELINUXTYPE=seedit
sysconfdir = /etc
prefix = /usr
DISTRO = COS4
CONVERTER=/usr/local/bin/seedit-converter
LOADPOLICY=/usr/sbin/load_policy
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
FCFILE=./distro/$(DISTRO)/dynamic_contexts
SPDLSPEC=./src/base_policy/spdl_spec.xml

dir:
	mkdir -p $(POLICYROOT)/policy
	mkdir -p $(POLICYROOT)/users/
	mkdir -p $(POLICYROOT)/contexts/files
	mkdir -p $(POLICYROOT)/contexts/files
	mkdir -p $(POLICYROOT)/contexts/users
	mkdir -p $(SEEDITCONFROOT)/policy
	mkdir -p $(SEEDITCONFROOT)/converter
	mkdir -p $(SEEDITCONFROOT)/converter/conf
	mkdir -p $(SEEDITCONFROOT)/converter/sepolicy

policy:  
	mkdir -p policy
	if [ -e src/simplified_policy.$(DISTRO) ];then \
		cp -r src/simplified_policy.$(DISTRO) policy/simplified_policy;\
	else \
		cp -r src/simplified_policy policy/simplified_policy;\
	fi

	cp -r /etc/seedit/converter/conf/base_policy policy/
	cp -r /etc/seedit/converter/conf/macros policy/

	if [ -e src/Makefile.$(DISTRO) ];then \
		cp src/Makefile.$(DISTRO) policy/Makefile;\
	else \
		cp src/Makefile policy/Makefile;\
	fi


	cd policy ;make 
	if [ -e $(FCFILE) ] ; then cat $(FCFILE) >> policy/sepolicy/file_contexts; fi
install: policy dir
	cp policy/Makefile  $(SEEDITCONFROOT)/converter/
	cp -r policy/simplified_policy/*  $(SEEDITCONFROOT)/policy
	cp src/setrans.conf	$(POLICYROOT)

	if [ -e $(POLICYROOT)/contexts/files/file_contexts ]; then \
		cp $(POLICYROOT)/contexts/files/file_contexts $(POLICYROOT)/contexts/files/file_contexts.old;\
	fi
	cd policy;make install 

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

