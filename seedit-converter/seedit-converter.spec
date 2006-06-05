%define distro FC5
Summary: Compliler for simplified policy
Name: seedit-converter
Version: 2.0.0.b4
Release: %{distro} 
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
%__make DISTRO=%{distro}

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_bindir}/seedit-converter
%{_bindir}/audit2spdl
%{_bindir}/seedit-spdl2xml
%{_bindir}/seedit-xml2spdl
%{_sbindir}/seedit-rbac
%{_sbindir}/seedit-load
%{_sbindir}/seedit-restorecon
%{_bindir}/seedit-unconfined
%{_bindir}/seedit-template
%{_libdir}/seedit/*

%changelog
* Tue Apr 18 2006 Yuichi Nakamura<ynakam@gwu.edu> 1.4.0
* Wed Feb 23  2006 Yuichi Nakamura<ynakam@gwu.edu> 1.3.3
* Wed Feb 1  2006 Yuichi Nakamura<ynakam@gwu.edu> 1.3.2
XML support:seedit-export, seedit-import
* Tue Jan 17 2006 Yuichi Nakamura<ynakam@gwu.edu> 1.3.1
audit2spdl
* Fri Jan 13 2006 Yuichi Nakamura<ynakam@gwu.edu> 1.3.0
Support new file permissions
* Tue Aug 30 2005 Yuichi Nakamura<ynakam@gwu.edu> 1.2.0
Fixed some bugs.
* Wed Jul 20 2005 Yuichi Nakamura<ynakam@gwu.edu> 1.1.0
Cron support
* Sun Jul 10 2005  Yuichi Nakamura <ynakam@gwu.edu> 1.0.0-1
- Initial version for RPM package.
