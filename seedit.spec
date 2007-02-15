%define buildnum 5
%define python_sitelib %(%{__python} -c 'from distutils import sysconfig; print sysconfig.get_python_lib()')
%define selinuxenabled /usr/sbin/selinuxenabled

%define selinuxconf %{_sysconfdir}/selinux/config
%define auditrules %{_sysconfdir}/audit/audit.rules
#Whether SELinux supports customizable_types, after FC5 "y"
%define customizable_types y
#Whether SELinux supports modular policy, after FC5 "y"
%define modular y
#Whether pam supports include syntax, after FC5 "y"
%define pam_include_support y  
#Whether audit support obj_type field, after FC6 "y"
%define audit_obj_type_support  y
#Version of sample policy file
%define sample_policy_type fc6

Name: seedit         
Version: 2.1.0
Release: %{buildnum}%{?dist}
Summary: SELinux Policy Editor:Core component
Group:  System Environment/Base        
License: GPL       
URL: http://seedit.sourceforge.net/
Source0: http://osdn.dl.sourceforge.jp/selpe/23577/%{name}-%{version}.tar.gz
Source1: seedit-gui.desktop
Source2: seedit-gui.png
Patch0: 2.1.0-5.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{betatag}-root-%(%{__id_u} -n)
BuildRequires:  libselinux-devel >= 1.19, libsepol-devel >= 1.1.1, byacc, flex
Requires:  checkpolicy, m4, audit, libselinux >= 1.19, libsepol >= 1.1.1
Provides: seedit-converter = %{version}-%{release}

%description
SELinux Policy Editor(SEEdit) is a tool to make SELinux easy.
SEEdit is composed of Simplified Policy, command line utils and GUI.
The main feature is Simplified Policy. 
Simplified Policy is written in Simplified Policy Description Language(SPDL).
SPDL hides detail of SELinux.
For detail, visit http://seedit.sourceforge.net/.
Command line utils is included in seedit package.

%prep
%setup -q
%patch0 -p0

%build
pushd core
make clean
make %{?_smp_mflags} CFLAGS="%{optflags}" CUSTOMIZABLE_TYPES=%{customizable_types} MODULAR=%{modular}
popd

%install
rm -rf %{buildroot}

pushd core
make install  DESTDIR=%{buildroot}  PYTHON_SITELIB=%{buildroot}/%{python_sitelib} CUSTOMIZABLE_TYPES=%{customizable_types}  MODULAR=%{modular}  AUDIT_OBJ_TYPE_SUPPORT=%{audit_obj_type_support}
popd

pushd policy
make install DESTDIR=%{buildroot}  DISTRO=%{sample_policy_type} SELINUXTYPE=seedit MODULAR=%{modular} AUDITRULES=%{auditrules} 
popd

pushd gui
make install DESTDIR=%{buildroot}  PYTHON_SITELIB=%{buildroot}/%{python_sitelib} PAM_INCLUDE_SUPPORT=%{pam_include_support}

#For Asianux2
#AX2 mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/applications
#AX2 install -p -m 0644 %{SOURCE1} ${RPM_BUILD_ROOT}%{_datadir}/applications
desktop-file-install --vendor "" --dir ${RPM_BUILD_ROOT}%{_datadir}/applications %{SOURCE1}


mkdir -p %{buildroot}%{_datadir}/pixmaps
install -p -m 0644 %{SOURCE2} ${RPM_BUILD_ROOT}%{_datadir}/pixmaps/seedit-gui.png
popd

#touch ghost files
touch ${RPM_BUILD_ROOT}%{_datadir}/%{name}/sepolicy/need-rbac-init
touch ${RPM_BUILD_ROOT}%{_datadir}/%{name}/sepolicy/need-init

%find_lang %{name}

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc README Changelog COPYING AUTHORS NEWS TODO
%{_bindir}/seedit-converter
%{_bindir}/audit2spdl
%{_sbindir}/seedit-rbac
%{_sbindir}/seedit-load
%{_sbindir}/seedit-restorecon
%{_bindir}/seedit-unconfined
%{_bindir}/seedit-template
%dir %{python_sitelib}/%{name}
%{python_sitelib}/%{name}/*.*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/Makefile
%{_datadir}/%{name}/macros
%{_datadir}/%{name}/base_policy
%dir %{_datadir}/%{name}/sepolicy
%{_datadir}/%{name}/seedit-load.conf

%package policy
Summary: SELinux Policy Editor: Sample simplified policy
Group:  System Environment/Base
Requires: %{name} = %{version}-%{release}

%description policy
Sample simplified policy for SEEdit.

%post policy
if [ $1 = 1 ]; then
	#Mark to initialize SELinux Policy Editor, when new install
	touch %{_datadir}/%{name}/sepolicy/need-init
fi

if [ $1 = 2 ]; then
	#Mark to initialize RBAC config when upgrade
	touch %{_datadir}/%{name}/sepolicy/need-rbac-init
fi

%postun policy
if [ $1 = 0 ]; then
	sed -i 's/^SELINUXTYPE=.*/SELINUXTYPE=targeted/g' %{_sysconfdir}/selinux/config
	if [ %{selinuxenabled} ]; then
		sed -i 's/^SELINUX=.*/SELINUX=permissive/g' %{_sysconfdir}/selinux/config
	fi
	touch /.autorelabel
fi

%files policy
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/policy
%config(noreplace) %{_sysconfdir}/selinux/%{name}
%{_datadir}/%{name}/initialize/
%{_sbindir}/seedit-init
%ghost %{_datadir}/%{name}/sepolicy/need-init
%ghost %{_datadir}/%{name}/sepolicy/need-rbac-init

%package gui
Summary: GUI for SELinux Policy Editor
Group: System Environment/Base
Requires: usermode
Requires: pygtk2
Requires: pam >= 0.80-9
BuildRequires: desktop-file-utils
BuildRequires:  gettext
Requires: %{name} = %{version}-%{release}, %{name}-policy = %{version}-%{release}

%description gui
X based GUI for SELinux Policy Editor

%files gui -f %{name}.lang
%defattr(-,root,root,-)
%{_bindir}/seedit-gui
%{_sbindir}/seedit-gui
%{_sbindir}/seedit-gui-status
%{_sbindir}/seedit-gui-domain-manager
%{_sbindir}/seedit-gui-role-manager
%{_sbindir}/seedit-gui-generate-policy
%{_sbindir}/seedit-gui-edit
%{_sbindir}/seedit-gui-load
%{python_sitelib}/%{name}/ui
%{_datadir}/icons/%{name}
%{_datadir}/applications/seedit-gui.desktop
%config(noreplace) %{_sysconfdir}/security/console.apps/seedit-gui
%config(noreplace) %{_sysconfdir}/pam.d/seedit-gui
%{_datadir}/pixmaps/seedit-gui.png


%changelog
* Fri Feb 16 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-5
 - SELINUX= is set permissive when uninstall,
because relabel fails in enforcing mode.
 - Modified path to seedit-load.conf

* Thu Feb 15 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-4
 - Fixed bug, seedit-converter did not work when "//" is included in path

* Fri Feb 9 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-3
 - Fixed build failure

* Fri Feb 9 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-2
 - Fixed build failure

* Tue Feb 6 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-1
 - Fixed bug in RBAC
 - Fixed installer for Asianux

* Wed Jan 31 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.16.beta7
 - Fixed for CentOS4, package build failed.

* Sat Jan 27 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.15.beta6.7
 - Fixed Requires
 - Fixed makefiles to preserve timestamps.

* Fri Jan 26 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.14.beta6.6
 - Fixed spec file, to more fit Fedora Extras.
 - Fixed makefiles to preserve timestamps.

* Thu Jan 25 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.13.beta6.5
 - Prepared rbac-on flag.

* Thu Jan 25 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.12.beta6.4
 - Fixed bug in upgrade.

* Wed Jan 24 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.11.beta6.3
 - Fixed bug that seedit-gui does not start.

* Tue Jan 23 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.10.beta6.2
 - Fixed spec file, to more fit Fedora Extras.
   
* Thu Jan 18 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.9.beta6.2
 - Fixed spec file, Makefiles, to more fit Fedora Extras.
   
* Thu Jan 18 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.8.beta6.1
 - Cleaned spec file , to fit Fedora Extras.
   
* Fri Jan 12 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.7.beta6
 - Fixed spec file to use desktop-file-install
 - Modified paths to use macros

* Wed Jan 10 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.6.beta6
 - Merged 3 spec files into 1 spec file(seedit.spec).
 
* Thu Dec 28 2006 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.1.beta5
  Added Generate more policy button.
  Fixed bug of audit2spdl module.

* Fri Nov 10 2006 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.1.beta4
 Change of install path, clean ups to submit FE.
 Merged icons from Shane M. Coughlan.

* Tue Sep 26 2006 Yuichi Nakamura 2.0.2
Merged changes(about lanugage changes) from Shane M. Coughlan.

* Tue Sep 19 2006 Yuichi Nakamura 2.0.1-1
Fixed bug for RBAC(default_cotnexts)
seedit-converter generates userhelper_contexts
Fixed bug for Cent OS 4
Merged clean up about copyright statement from Shane M. Coughlan.

* Fri Aug 25 2006 Yuichi Nakamura 2.0.0-2
Fixed bug. rename was integrated into c permission, e is correct.

* Mon Jul 2 2006 Yuichi Nakamura<himainu-ynakam@miomio.jp> 2.0.0
- Initial version

