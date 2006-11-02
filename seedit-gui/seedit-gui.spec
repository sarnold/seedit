%define python_ver 2.4
Summary: GUI for SELinux  Policy Editor
Name: seedit-gui
Version: 2.1.0.b4
Release:  1
License: GPL
Group: System Environment/Base
URL: http://sedit.sourceforge.net/
Source0: %{name}-%{version}-%{release}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch
Requires: seedit-converter >= 2.1.0, seedit-policy >= 2.1.0,audit,pygtk2


%description
X Window based GUI for SELinux Policy Editor

%prep
%setup -q

%build
make clean
%__make 

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall PYTHON_VER=%{python_ver}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_bindir}/seedit-gui
%{_sbindir}/seedit-gui
%{_sbindir}/seedit-gui-status
%{_sbindir}/seedit-gui-domain-manager
%{_sbindir}/seedit-gui-role-manager
%{_sbindir}/seedit-gui-generate-policy
%{_sbindir}/seedit-gui-edit
%{_sbindir}/seedit-gui-load
%{_libdir}/seedit/*
%{_libdir}/python%{python_ver}/site-packages
/usr/share/icons/seedit/*
/usr/share/applications/seedit-gui.desktop
/usr/share/locale/*
/etc/security/console.apps/seedit-gui
/usr/share/pixmaps/seedit-gui.png

%changelog
* Tue Sep 26 2006 Yuichi Nakamura 2.0.2
Merged changes(about lanugage changes) from Shane M. Coughlan.

* Tue Sep 19 2006 Yuichi Nakamura 2.0.1
Fixed bug for Cent OS 4
Merged clean up about copyright statement from Shane M. Coughlan.

* Mon Jul 3 2006 Yuichi Nakamura<himainu-ynakam@miomio.jp> 2.0.0
- Initial version

