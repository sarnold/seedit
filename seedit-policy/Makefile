# $Id: Makefile,v 1.8 2006/05/05 16:05:36 ynakam Exp $

include build.conf
sysconfdir = /etc
prefix = /usr
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

src/macros/seedit_macros.te:  $(SPDLSPEC) src/base_policy/access_vectors
	./scripts/genmacro.py -i $(SPDLSPEC) -m macro -o src/macros/seedit_macros.te
#	./scripts/gen_allow_admin_all_macro.pl -i src/base_policy/ >> ./src/macros/seedit_macros.te

./src/base_policy/unsupported.te: $(SPDLSPEC)
	./scripts/genmacro.py -i $(SPDLSPEC) -m unsupported > ./src/base_policy/unsupported.te

macro: ./src/macros/seedit_macros.te
unsupport: ./src/base_policy/unsupported.te

policydir:  macro unsupport 
	mkdir -p policy
	cp -r src/base_policy policy
	cp -r src/macros policy
	cp -r src/simplified_policy policy
	rm -rf policy/base_policy/CVS
	rm -rf policy/macros/CVS
	rm -rf policy/simplified_policy/CVS

	./scripts/genmacro.py -i src/base_policy/spdl_spec.xml -m expand > policy/base_policy/spdl_spec.xml

policy:  policydir
#	./scripts/mkinstfiles.sh $(DISTRO) $(DEVELFLAG) $(POLICYTYPE) $(SELINUXTYPE);
#	cp -r ./src/simplified_policy policy/simplified_policy
	mkdir -p policy
	if [ -e src/Makefile.$(DISTRO) ];then \
		cp src/Makefile.$(DISTRO) policy/Makefile;\
	else \
		cp src/Makefile policy/Makefile;\
	fi
	cd policy ;make 
	if [ -e $(FCFILE) ] ; then cat $(FCFILE) >> policy/sepolicy/file_contexts; fi
install: policy dir
	cp -r policy/base_policy $(SEEDITCONFROOT)/converter/conf
	cp -r policy/macros $(SEEDITCONFROOT)/converter/conf
	cp policy/Makefile  $(SEEDITCONFROOT)/converter/
	cp -r policy/simplified_policy/*  $(SEEDITCONFROOT)/policy
	cd policy;make install contexts
	cp $(POLICYROOT)/contexts/files/file_contexts.all $(POLICYROOT)/contexts/files/file_contexts.all.old
	cp -r $(BASEPOLICYDIR)/contexts/*  $(POLICYROOT)/contexts
	rm $(POLICYROOT)/contexts/customizable_types
	touch $(POLICYROOT)/users/system.users
	touch $(POLICYROOT)/users/local.users

postconfig: install
	cat $(SELINUXCONF) |sed -e 's/^SELINUX=.*$$/SELINUX=permissive/'|sed -e 's/^SELINUXTYPE=.*$$/SELINUXTYPE=$(SELINUXTYPE)/' >$(SELINUXCONF).tmp
	mv $(SELINUXCONF) $(SELINUXCONF).orig
	mv $(SELINUXCONF).tmp $(SELINUXCONF)
	touch /.autorelabel
	$(RESTORECON) $(SELINUXCONF)

doc:./doc/permission_integrate.pdf

./doc/permission_integrate.pdf: $(SPDLSPEC) doc/permission_integrate.tex
	./scripts/genmacro.py -i $(SPDLSPEC) -m latex -o doc/table.tex
	cd doc;	latex permission_integrate.tex;\
	latex permission_integrate.tex;\
	latex permission_integrate.tex;\
	latex2html -show_section_numbers -link 2 -split 0 permission_integrate.tex;\
	dvipdf  permission_integrate.dvi

clean:
	rm -rf policy doc/*.aux doc/*.toc doc/*.pdf src/base_policy/unsupported.te src/macros/seedit_macros.te

