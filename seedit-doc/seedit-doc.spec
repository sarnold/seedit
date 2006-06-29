Summary: Documents for SELinux Policy Editor
Name: seedit-doc
Version: 2.0.0.rc1
Release: 1
License: GPL
Group: Documentation
URL: http://seedit.sourceforge.net/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch
BuildRequires: latex2html

%description

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
/usr/share/doc/seedit

%changelog
* Wed Jun 28 2005 Yuichi Nakamura <ynakam@gwu.edu> - doc-1
- Initial build.

