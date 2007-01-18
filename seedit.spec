%define betatag beta6.1
%define buildnum 8
%define python_ver 2.4
%define selinuxconf /etc/selinux/config
%define auditrules /etc/audit/audit.rules
#Whether SELinux supports customizable_types, after FC5 "y"
%define customizable_types y
#Whether SELinux supports modular policy, after FC5 "y"
%define modular y
#Whether pam supports include syntax, after FC5 "y"
%define pam_include_support y  
#Version of sample policy file
%define sample_policy_type fc6 

Name: seedit         
Version: 2.1.0
Release: 0.%{buildnum}.%{betatag}%{?dist}
Summary: SELinux Policy Editor:Core component
Group:  System Environment/Base        
License: GPL       
URL: http://seedit.sourceforge.net/
Source0: http://prdownloads.sourceforge.jp/selpe/23577/%{name}-%{version}-%{betatag}.tar.gz
Source1: seedit-gui.desktop
Source2: seedit-gui.png
BuildRoot: %{_tmppath}/%{name}-%{version}-%{betatag}-root-%(%{__id_u} -n)
BuildRequires:  libselinux-devel >= 1.19, libsepol-devel >= 1.1.1
Requires:  checkpolicy, m4, audit, libselinux >= 1.19, libsepol >= 1.1.1

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

%build
pushd core
make clean
make %{?_smp_mflags} PYTHON_VER=%{python_ver} CUSTOMIZABLE_TYPES=%{customizable_types} MODULAR=%{modular}
popd

%install
rm -rf $RPM_BUILD_ROOT

pushd core
make install  DESTDIR=$RPM_BUILD_ROOT  PYTHON_VER=%{python_ver} CUSTOMIZABLE_TYPES=%{customizable_types}  MODULAR=%{modular}
popd

pushd policy
make install DESTDIR=$RPM_BUILD_ROOT  DISTRO=%{sample_policy_type} SELINUXTYPE=seedit MODULAR=$MODULAR AUDITRULES=%{auditrules}
popd

pushd gui
make install DESTDIR=$RPM_BUILD_ROOT PYTHON_VER=%{python_ver} PAM_INCLUDE_SUPPORT=%{pam_include_support}

desktop-file-install --vendor fedora --dir ${RPM_BUILD_ROOT}%{_datadir}/applications  --add-category X-Fedora %{SOURCE1}

mkdir -p $RPM_BUILD_ROOT%{_datadir}/pixmaps
install -m 664 %{SOURCE2} ${RPM_BUILD_ROOT}%{_datadir}/pixmaps/seedit-gui.png
popd

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_bindir}/seedit-converter
%{_bindir}/audit2spdl
%{_sbindir}/seedit-rbac
%{_sbindir}/seedit-load
%{_sbindir}/seedit-restorecon
%{_bindir}/seedit-unconfined
%{_bindir}/seedit-template
%{_libdir}/python%{python_ver}/site-packages/seedit/*
%{_datadir}/seedit
%doc README
%doc Changelog
%doc COPYING
%doc AUTHORS
%doc NEWS
%doc TODO

%package policy
Summary: SELinux Policy Editor: Sample simplified policy
Group:  System Environment/Base
Requires: seedit >= 2.1.0

%description policy
Sample simplified policy for SEEdit.

%post policy
if [ $1 = 1 ]; then
	#Mark to initialize SELinux Policy Editor, when new install
	touch %{_datadir}/share/seedit/sepolicy/need-init
fi

if [ $1 = 2 ]; then
	#Mark to initialize RBAC config when upgrade
	touch %{_datadir}/share/seedit/sepolicy/need-rbac-init
fi

%postun policy
if [ $1 = 0 ]; then
	sed -i 's/^SELINUX=.*/SELINUX=permissive/g' %{_sysconfdir}/selinux/config
	sed -i 's/^SELINUXTYPE=.*/SELINUXTYPE=targeted/g' %{_sysconfdir}/selinux/config
	touch /.autorelabel
fi

%files policy
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/selinux/seedit
%config(noreplace) %{_sysconfdir}/seedit/policy
%{_datadir}/seedit/scripts/seedit-installhelper.sh
%{_datadir}/seedit/scripts/seedit-installhelper-include.sh
%{_datadir}/seedit/base_policy/contexts/dynamic_contexts
%{_sbindir}/seedit-init

%package gui
Summary: GUI for SELinux Policy Editor
Group: System Environment/Base
Requires: python >= 2.3
Requires: gnome-python2, pygtk2
BuildRequires: desktop-file-utils, gettext
Requires: seedit >= 2.1.0, seedit-policy >= 2.1.0


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
%{_libdir}/python%{python_ver}/site-packages/seedit/ui
%{_datadir}/icons/seedit
%{_datadir}/applications/fedora-seedit-gui.desktop
%config(noreplace) %{_sysconfdir}/security/console.apps/seedit-gui
%config(noreplace) %{_sysconfdir}/pam.d/seedit-gui
%{_datadir}/pixmaps/seedit-gui.png


%changelog
* Thu Jan 18 2007 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.8.beta6.1
 - Cleaned spec file 
   
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

