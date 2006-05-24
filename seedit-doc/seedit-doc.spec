Summary: Documents for SELinux Policy Editor(packages seedit-*)
Name: seedit-doc
Version: 1.2.0
Release: 1
License: GPL
Group: Documentation
URL: http://seedit.sourceforge.net/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch

%description

%prep
%setup -q

%build
make build
%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
/usr/share/doc/seedit-doc

%changelog
* Thu Aug 25 2005 Yuichi Nakamura <ynakam@gwu.edu> - doc-1
- Initial build.

