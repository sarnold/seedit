Summary: GUI for SELinux  Policy Editor
Name: seedit-gui
Version: 2.0.1
Release:  1
License: GPL
Group: System Environment/Base
URL: http://sedit.sourceforge.net/
Source0: %{name}-%{version}-%{release}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch
Requires: seedit-converter >= 2.0.1, seedit-policy >= 2.0.1,audit,pygtk2


%description
X Window based GUI for SELinux Policy Editor

%prep
%setup -q

%build
make clean
%__make 

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

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
/usr/share/icons/seedit/*
/usr/share/applications/seedit-gui.desktop
/usr/share/locale/*
/etc/security/console.apps/seedit-gui
/usr/share/pixmaps/seedit-gui.png

%changelog
* Tue Sep 19 2006 Yuichi Nakamura 2.0.1
Fixed bug for Cent OS 4

* Mon Jul 3 2006 Yuichi Nakamura<himainu-ynakam@miomio.jp> 2.0.0
- Initial version

