Summary: GUI for SELinux  Policy Editor
Name: seedit-gui
Version: 2.0.0.b5
Release:  1
License: GPL
Group: System Environment/Base
URL: http://sedit.sourceforge.net/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description

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
%{_sbindir}/seedit-gui
%{_sbindir}/seedit-gui-status
%{_sbindir}/seedit-gui-domain-manager
%{_sbindir}/seedit-gui-generate-policy
%{_libdir}/seedit/*
/usr/share/icons/seedit/*

%changelog
* Sun Jun 18 2006 Yuichi Nakamura<himainu-ynakam@miomio.jp> 2.0.0b5
Initial
