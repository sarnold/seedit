%define distro COS4
%define buildnum 1
%define python_ver 2.3
Summary: Compliler for simplified policy
Name: seedit-converter
Version: 2.1.0.b4
Release: %{buildnum}.%{distro}
License: GPL
Group: System Environment/Base
URL: http://sedit.sourceforge.net/
Source0: %{name}-%{version}-%{buildnum}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description
Compiler for simplified policy and utilities.

%prep
%setup -q

%build
make clean
%__make DISTRO=%{distro} PYTHON_VER=%{python_ver}

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall DISTRO=%{distro} PYTHON_VER=%{python_ver}

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
%{_libdir}/python%{python_ver}/site-packages/seedit/*
/etc/pam.d/seedit-gui
/usr/share/seedit


%changelog
* Tue Sep 19 2006 Yuichi Nakamura 2.0.1-1
Fixed bug for RBAC(default_cotnexts)
Converter will generate userhelper_contexts

* Fri Aug 25 2006 Yuichi Nakamura 2.0.0-2
Fixed bug. rename was integrated into c permission, e is correct.

* Mon Jul 2 2006 Yuichi Nakamura<himainu-ynakam@miomio.jp> 2.0.0
- Initial version

