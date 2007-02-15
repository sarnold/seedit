# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

SELINUXTYPE=seedit
DISTRO ?= fc6
sysconfdir = /etc
prefix ?= /usr
CONVERTER=/usr/bin/seedit-converter
LOADPOLICY=/usr/sbin/load_policy
CHECKPOLICY=/usr/bin/checkpolicy
FIXFILES=/sbin/fixfiles
RESTORECON=/sbin/restorecon
SELINUXCONF=$(sysconfdir)/selinux/config
POLICYROOT=$(sysconfdir)/selinux/$(SELINUXTYPE)
SEEDITCONFROOT=$(prefix)/share/seedit
CONFDIR=./simplified_policy
BASEPOLICYDIR=./base_policy
MACRODIR=./macros
OUTDIR =./sepolicy
FCFILE=./distro/$(DISTRO)/dynamic_contexts
SPDLSPEC=./base_policy/spdl_spec.xml
BUILD_ROOT_DIR=$(prefix)/share/seedit
MODULAR ?= y
AUDIT_OBJ_TYPE_SUPPORT ?= y
GHOST_FILES="base.mod file_contexts policy.conf base.pp file_contexts.m4 unconfined_domains confined_domains  file_contexts.m4.old  userhelper_context customizable_types  generated.conf userhelper_context.m4"

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


seedit-load.conf:
	echo "audit_chdir $(AUDIT_OBJ_TYPE_SUPPORT)">seedit-load.conf

install:all seedit-load.conf
	mkdir -p $(BUILD_ROOT_DIR)/sepolicy
	mkdir -p $(SEEDITCONFROOT)
	mkdir -p $(sysconfdir)/seedit
	install -p -m 0644 seedit-load.conf  $(SEEDITCONFROOT)
	cp -p -r base_policy $(SEEDITCONFROOT)
	cp -p -r macros $(SEEDITCONFROOT)
	mv $(SEEDITCONFROOT)/base_policy/spdl_spec.xml.expand  $(SEEDITCONFROOT)/base_policy/spdl_spec.xml

	if [ $(MODULAR) = "y" ];then \
		install -p -m 644 makefiles/Makefile.modular $(BUILD_ROOT_DIR)/Makefile;\
	else \
		install -p -m 644 makefiles/Makefile.mono $(BUILD_ROOT_DIR)/Makefile;\
	fi

#touch files for rpm package(%ghost section)
#	cd $(BUILD_ROOT_DIR)/sepolicy;\
#	touch $GHOST_FILES

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
