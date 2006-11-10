%define buildnum 1
%define betatag beta4
%define distro COS4
%define python_ver 2.3
%define customizable_types n

Summary: SELinux Policy Editor:SPDL compiler
Name: seedit-converter
Version: 2.1.0
Release: 0.%{buildnum}.%{betatag}.%{distro}
License: GPL
Group: System Environment/Base
URL: http://seedit.sourceforge.net/
Source0: %{name}-%{version}-%{betatag}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{betatag}-root-%(%{__id_u} -n)

%description
This is component of SELinux Policy Editor(seedit).
seedit is a tool to make SELinux easy.
SPDL compiler and utilities are packed.
SPDL is a easy configuration language for SELinux,
SPDL is converted by SPDL compiler.

%prep
%setup -q

%build
make clean
make DISTRO=%{distro} PYTHON_VER=%{python_ver} CUSTOMIZABLE_TYPES=%{customizable_types}

%install
rm -rf $RPM_BUILD_ROOT
make install  DESTDIR="%{buildroot}" DISTRO=%{distro} PYTHON_VER=%{python_ver} CUSTOMIZABLE_TYPES=%{customizable_types}

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
/usr/share/seedit
%doc README
%doc Changelog
%doc COPYING


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

