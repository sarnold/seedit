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
HTML based documents of SELinux Policy Editor

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
* Mon Jul 3 2006 Yuichi Nakamura<himainu-ynakam@miomio.jp> 2.0.0
- Initial version

