%define buildnum 1
%define betatag beta5
%define distro cos4
%define python_ver 2.3
%define customizable_types n
%define selinuxconf /etc/selinux/config
%define auditrules /etc/audit/audit.rules
%define modular y
%define pam_include_support n

Summary: SELinux Policy Editor:SPDL compiler
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
Obsoletes: seedit-converter

%description
SELinux Policy Editor(SEEdit) is a tool to make SELinux easy.
Command line utils of SEEdit is packed here.

%prep
%setup -q

%build
DISTRO=%{distro} 
MODULAR=%{modular}
cd core
make clean
make DISTRO=%{distro} PYTHON_VER=%{python_ver} CUSTOMIZABLE_TYPES=%{customizable_types} MODULAR=%{modular}
cd ..

cd gui
make clean
make 
cd ..

%install
DISTRO=%{distro} 
MODULAR=%{modular}
rm -rf $RPM_BUILD_ROOT
cd core
make install  DESTDIR="%{buildroot}" DISTRO=%{distro} PYTHON_VER=%{python_ver} CUSTOMIZABLE_TYPES=%{customizable_types}  MODULAR=%{modular}
cd ..

cd policy
make install DESTDIR="%{buildroot}" CONVERTER=/usr/bin/seedit-converter DISTRO=$DISTRO  DEVELFLAG=0 SELINUXTYPE=seedit MODULAR=$MODULAR AUDITRULES=%{auditrules}
cd ..

cd gui
make install DESTDIR="%{buildroot}" PYTHON_VER=%{python_ver} DISTRO=%{distro} PAM_INCLUDE_SUPPORT=%{pam_include_support}

install -d -m 755 ${RPM_BUILD_ROOT}%{_datadir}/applications
install -m 664 %{SOURCE1} ${RPM_BUILD_ROOT}%{_datadir}/applications/seedit-gui.desktop
mkdir -p $RPM_BUILD_ROOT/usr/share/pixmaps
install -m 664 %{SOURCE2} ${RPM_BUILD_ROOT}/usr/share/pixmaps/seedit-gui.png
cd ..
%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT 

%files -f %{name}.lang
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

%files policy
%defattr(-,root,root,-)
%config(noreplace) /etc/selinux/seedit
%config(noreplace) /etc/seedit/policy
/usr/share/seedit/scripts/seedit-installhelper.sh
/usr/share/seedit/scripts/seedit-installhelper-include.sh
/usr/sbin/seedit-init

%package gui
Summary: GUI for SELinux Policy Editor
Group: System Environment/Base
URL: http://sedit.sourceforge.net/
Requires: seedit >= 2.1.0, seedit-policy >= 2.1.0,audit,pygtk2

%description gui
X based GUI for SELinux Policy Editor

%files gui 
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

%changelog
* Fri Nov 10 2006 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.1.beta4
Change of install path, clean ups to submit FE.

* Tue Sep 19 2006 Yuichi Nakamura 2.0.1-1
Fixed bug for RBAC(default_cotnexts)
Converter will generate userhelper_contexts

* Fri Aug 25 2006 Yuichi Nakamura 2.0.0-2
Fixed bug. rename was integrated into c permission, e is correct.

* Mon Jul 2 2006 Yuichi Nakamura<himainu-ynakam@miomio.jp> 2.0.0
- Initial version

