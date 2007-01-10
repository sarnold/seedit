%define betatag beta6
%define buildnum 6
#Configure these values according to target distro, see INSTALL for detail
%define distro fc6
%define python_ver 2.4
%define customizable_types y
%define selinuxconf /etc/selinux/config
%define auditrules /etc/audit/audit.rules
%define modular y
%define pam_include_support y

#policy,gui subpackages are build only when arch is "noarch"
%define buildpolicy 0
%define buildgui 0
%define buildcore 1
%ifarch noarch
%define buildpolicy 1 
%define buildgui 1
%define buildcore 0
%endif

Summary: SELinux Policy Editor:Core component
Name: seedit
Version: 2.1.0
Release: 0.%{buildnum}.%{betatag}.%{distro}
License: GPL
Group: System Environment/Base
URL: http://seedit.sourceforge.net/
Source0: %{name}-%{version}-%{betatag}.tar.gz
Source1: seedit-gui.desktop
Source2: seedit-gui.png
BuildRoot: %{_tmppath}/%{name}-%{version}-%{betatag}-root-%(%{__id_u} -n)
Provides:  seedit-converter = %{version}-%{release}
Obsoletes: seedit-converter <= 2.0.0-0.5

%description
SELinux Policy Editor(SEEdit) is a tool to make SELinux easy.
Command line utils of SEEdit is provided by this package
For detail, visit http://seedit.sourceforge.net/.

%prep
%setup -q

%build
DISTRO=%{distro} 
MODULAR=%{modular}
%if %{buildcore}
cd core
make clean
make DISTRO=%{distro} PYTHON_VER=%{python_ver} CUSTOMIZABLE_TYPES=%{customizable_types} MODULAR=%{modular}
cd ..
%endif

%if %{buildgui}
cd gui
make clean
make 
cd ..
%endif

%install
DISTRO=%{distro} 
MODULAR=%{modular}
rm -rf %{buildroot}

%if %{buildcore}
cd core
make install  DESTDIR="%{buildroot}" DISTRO=%{distro} PYTHON_VER=%{python_ver} CUSTOMIZABLE_TYPES=%{customizable_types}  MODULAR=%{modular}
cd ..
%endif

%if %{buildpolicy}
cd policy
make install DESTDIR="%{buildroot}" CONVERTER=/usr/bin/seedit-converter DISTRO=$DISTRO  DEVELFLAG=0 SELINUXTYPE=seedit MODULAR=$MODULAR AUDITRULES=%{auditrules}
cd ..
%endif

%if %{buildgui}
cd gui
make install DESTDIR="%{buildroot}" PYTHON_VER=%{python_ver} DISTRO=%{distro} PAM_INCLUDE_SUPPORT=%{pam_include_support}

install -d -m 755 ${RPM_BUILD_ROOT}%{_datadir}/applications
install -m 664 %{SOURCE1} ${RPM_BUILD_ROOT}%{_datadir}/applications/seedit-gui.desktop
mkdir -p $RPM_BUILD_ROOT/usr/share/pixmaps
install -m 664 %{SOURCE2} ${RPM_BUILD_ROOT}/usr/share/pixmaps/seedit-gui.png
cd ..
%find_lang %{name}
%endif

%clean
rm -rf %{buildroot}

%if %{buildcore}
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
/usr/share/seedit
%doc README
%doc Changelog
%doc COPYING
%doc AUTHORS
%doc NEWS
%doc TODO
%endif

%package policy
Summary: SELinux Policy Editor: Sample simplified policy
Group:  System Environment/Base
Requires: seedit >= 2.1.0, checkpolicy,m4,audit

%description policy
Sample simplified policy for SEEdit.

%post policy
if [ $1 = 1 ]; then
	#Mark to initialize SELinux Policy Editor, when new install
	touch /usr/share/seedit/sepolicy/need-init
fi

if [ $1 = 2 ]; then
	#Mark to initialize RBAC config when upgrade
	touch /usr/share/seedit/sepolicy/need-rbac-init
fi

%postun policy
if [ $1 = 0 ]; then
	sed -i 's/^SELINUX=.*/SELINUX=permissive/g' /etc/selinux/config
	sed -i 's/^SELINUXTYPE=.*/SELINUXTYPE=targeted/g' /etc/selinux/config
	touch /.autorelabel
fi

%if %{buildpolicy}
%files policy
%defattr(-,root,root,-)
%config(noreplace) /etc/selinux/seedit
%config(noreplace) /etc/seedit/policy
/usr/share/seedit/scripts/seedit-installhelper.sh
/usr/share/seedit/scripts/seedit-installhelper-include.sh
/usr/sbin/seedit-init
%endif

%package gui
Summary: GUI for SELinux Policy Editor
Group: System Environment/Base
Requires: seedit >= 2.1.0, seedit-policy >= 2.1.0,audit,pygtk2

%description gui
X based GUI for SELinux Policy Editor

%if %{buildgui}
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
/usr/share/icons/seedit
/usr/share/applications/seedit-gui.desktop
%config(noreplace) /etc/security/console.apps/seedit-gui
%config(noreplace) /etc/pam.d/seedit-gui
/usr/share/pixmaps/seedit-gui.png
%endif

%changelog
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

