# $Id: Makefile,v 1.11 2006/04/28 16:48:28 ynakam Exp $
# (c) Yuichi Nakamura himainu-ynakam@miomio.jp
sysconfdir =/etc
CONVERTER=/usr/bin/seedit-converter
LOADPOLICY=/usr/sbin/load_policy
CHECKPOLICY=/usr/bin/checkpolicy
GENHOMEDIRCON=/usr/sbin/genhomedircon
FIXFILES=/sbin/fixfiles
RESTORECON=/usr/sbin/seedit-restorecon
SELINUXTYPE=seedit
POLICYROOT=$(sysconfdir)/selinux/$(SELINUXTYPE)
POLICYDIR=$(POLICYROOT)/policy
CONTEXTSDIR=$(POLICYROOT)/contexts
CONFDIR=./simplified_policy
BASEPOLICYDIR=./base_policy
MACRODIR=./macros
OUTDIR =./sepolicy
INSTALL_PATH = $(POLICYROOT)
SELINUXCONF=$(sysconfdir)/selinux/config

DEFAULT_POLICYVER=18
POLICYVER := $(shell $(CHECKPOLICY)  -V |cut -f 1 -d ' ')
ifeq ($(POLICYVER),)
POLICYVER=$(DEFAULT_POLICYVER)
endif

ALL_FILE_CONTEXTS=  $(CONTEXTSDIR)/files/file_contexts.all
OLD_ALL_FILE_CONTEXTS=  $(CONTEXTSDIR)/files/file_contexts.all.old

policy:
	mkdir -p $(OUTDIR);
	m4 -s $(CONFDIR)/*.sp >$(CONFDIR)/all.sp;
	$(CONVERTER) -i $(CONFDIR)/all.sp -o $(OUTDIR) -b $(BASEPOLICYDIR) -I $(CONFDIR)/include ;
	m4 -Imacros -s $(MACRODIR)/*.te $(OUTDIR)/generated.conf > $(OUTDIR)/policy.conf;
	$(CHECKPOLICY) -o $(OUTDIR)/policy.$(POLICYVER) -c $(POLICYVER) $(OUTDIR)/policy.conf

install: policy
	cp $(OUTDIR)/policy.$(POLICYVER) $(POLICYDIR)
	cp $(OUTDIR)/unconfined_domains $(POLICYDIR)
	cp $(OUTDIR)/file_contexts $(CONTEXTSDIR)/files/
	cp $(OUTDIR)/homedir_template $(CONTEXTSDIR)/files/
	cp $(OUTDIR)/customizable_types $(CONTEXTSDIR)
	cp -r $(BASEPOLICYDIR)/contexts/*  $(CONTEXTSDIR) 

contexts: install
	$(GENHOMEDIRCON) -t $(SELINUXTYPE)
	cd $(CONTEXTSDIR)/files;\
	grep -v "<<none>>" file_contexts.homedirs > tmp;\
	grep -v -e "^/root" tmp > tmp2;\
	rm tmp; mv tmp2 file_contexts.homedirs;\
	cat file_contexts file_contexts.homedirs > $(ALL_FILE_CONTEXTS)	

relabel: contexts
	$(LOADPOLICY) $(POLICYDIR)/policy.$(POLICYVER)
	$(FIXFILES) -F restore
	cp $(ALL_FILE_CONTEXTS) $(OLD_ALL_FILE_CONTEXTS)

diffrelabel: contexts
	if [ -e fcdiff.tmp ] ; then \
		exec 3< fcdiff.tmp;\
		while read FL 0<&3; do \
	  	if [ -e $$FL ] ; then \
	    		$(RESTORECON) $$FL -R -vv;\
		fi;\
		done; \
		exec 3<&-;\
	fi;
	$(LOADPOLICY) $(POLICYDIR)/policy.$(POLICYVER)
	diff $(OLD_ALL_FILE_CONTEXTS) $(ALL_FILE_CONTEXTS) -r|grep -e "^[<>]"|sed -e 's/^[><][ \t]*//'|sed -e 's/[ \t]\+.*//'|sed -e 's/(.*//'|sort|sed s/"\[\^\/\]"//g > fcdiff.tmp
	exec 3< fcdiff.tmp;\
	while read FL 0<&3; do \
	  if [ -e $$FL ] ; then \
	    $(RESTORECON) $$FL -R -vv;\
	  fi;\
	done; \
	exec 3<&-;\
	cp $(ALL_FILE_CONTEXTS) $(OLD_ALL_FILE_CONTEXTS)
	rm fcdiff.tmp


