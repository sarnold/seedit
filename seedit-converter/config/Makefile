#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura
#! 
#! This program is free software; you can redistribute it and/or modify
#! it under the terms of the GNU General Public License as published by
#! the Free Software Foundation; either version 2 of the License, or
#! (at your option) any later version.
#! 
#! This program is distributed in the hope that it will be useful,
#! but WITHOUT ANY WARRANTY; without even the implied warranty of
#! MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#! GNU General Public License for more details.
#! 
#! You should have received a copy of the GNU General Public License
#! along with this program; if not, write to the Free Software
#! Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

SELINUXTYPE=seedit
DISTRO=FC5
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
CONFDIR=./simplified_policy
BASEPOLICYDIR=./base_policy
MACRODIR=./macros
OUTDIR =./sepolicy
FCFILE=./distro/$(DISTRO)/dynamic_contexts
SPDLSPEC=./base_policy/spdl_spec.xml

all:conf

macros/seedit_macros.te:  $(SPDLSPEC) base_policy/access_vectors
	./scripts/genmacro.py -i $(SPDLSPEC) -m macro -o macros/seedit_macros.te
#	./scripts/gen_allow_admin_all_macro.pl -i base_policy/ >> ./macros/seedit_macros.te

./base_policy/unsupported.te: $(SPDLSPEC)
	./scripts/genmacro.py -i $(SPDLSPEC) -m unsupported > ./base_policy/unsupported.te

macro: ./macros/seedit_macros.te
unsupport: ./base_policy/unsupported.te


conf: macro unsupport	

	./scripts/genmacro.py -i base_policy/spdl_spec.xml -m expand > base_policy/spdl_spec.xml.expand


install:all	
	mkdir -p $(SEEDITCONFROOT)/policy
	mkdir -p $(SEEDITCONFROOT)/converter
	mkdir -p $(SEEDITCONFROOT)/converter/conf
	mkdir -p $(SEEDITCONFROOT)/converter/sepolicy
	cp -r base_policy $(SEEDITCONFROOT)/converter/conf
	cp -r macros $(SEEDITCONFROOT)/converter/conf
	mv $(SEEDITCONFROOT)/converter/conf/base_policy/spdl_spec.xml.expand  $(SEEDITCONFROOT)/converter/conf/base_policy/spdl_spec.xml
	mkdir -p $(sysconfdir)/pam.d
	install -m 744 pam.d/seedit-gui.$(DISTRO)   $(sysconfdir)/pam.d/seedit-gui
	if [ -e makefiles/Makefile.$(DISTRO) ];then \
		install -m 744 makefiles/Makefile.$(DISTRO) $(SEEDITCONFROOT)/converter/Makefile;\
	else \
		install -m 744 makefiles/Makefile $(SEEDITCONFROOT)/converter;\
	fi

doc:./doc/permission_integrate.pdf

./doc/permission_integrate.pdf: $(SPDLSPEC) doc/permission_integrate.tex
	./scripts/genmacro.py -i $(SPDLSPEC) -m latex -o doc/table.tex
	cd doc;	latex permission_integrate.tex;\
	latex permission_integrate.tex;\
	latex permission_integrate.tex;\
	latex2html -show_section_numbers -link 2  permission_integrate.tex;\
	dvipdf  permission_integrate.dvi

clean:
	rm -rf policy doc/*.aux doc/*.toc doc/*.pdf base_policy/unsupported.te macros/seedit_macros.te
