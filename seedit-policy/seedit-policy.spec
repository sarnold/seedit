%define distro fc6
%define betatag beta4
%define buildnum 1

%define selinuxconf /etc/selinux/config
%define auditrules /etc/audit/audit.rules
%define installhelper /usr/share/seedit/scripts/seedit-installhelper.sh
%define modular y

Summary: SELinux Policy Editor: Simplified Policy
Name: seedit-policy
Version: 2.1.0
Release: 0.%{buildnum}.%{betatag}.%{distro}
License: GPL
Group:  System Environment/Base
URL:  http://seedit.sourceforge.net/
Source0: seedit-policy-%{version}-%{betatag}.tar.gz
BuildRoot: %{_tmppath}/seedit-policy-%{version}-%{betatag}-root-%(%{__id_u} -n)
BuildArch: noarch
Requires: seedit-converter >= 2.1.0, checkpolicy,m4,audit
BuildRequires:m4

%description
Component of SELinux Policy Editor(seedit).
seedit makes SELinux easy. 
This package is about
Simplified policy for SELinux.
Simplified policy is written by SPDL.
SPDL provides simplified syntax to describe SELinux policy,
it is converted into usual SELinux policy by commands 
included in seedit-converter.

%prep
%setup -q -n seedit-policy-%{version}

%build

%install
rm -rf $RPM_BUILD_ROOT
DISTRO=%{distro} 
MODULAR=%{modular}
make install DESTDIR="%{buildroot}" CONVERTER=/usr/bin/seedit-converter DISTRO=$DISTRO  DEVELFLAG=0 SELINUXTYPE=seedit MODULAR=$MODULAR AUDITRULES=%{auditrules}

%pre
if [ $1 = 2 ]; then
	touch /usr/share/seedit/sepolicy/need-rbac-init
fi

%post
if [ $1 = 1 ]; then
	#Mark to initialize SELinux Policy Editor
	touch /usr/share/seedit/sepolicy/need-init
fi


%preun

if [ $1 = 0 ]; then
	#Go back to targeted policy, automatic relabel
	%{installhelper} uninstall
fi


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%config(noreplace) /etc/selinux/seedit
%config(noreplace) /etc/seedit/policy
/usr/share/seedit/scripts/seedit-installhelper.sh
/usr/share/seedit/scripts/seedit-installhelper-include.sh
/usr/sbin/seedit-init
%doc README
%doc Changelog
%doc COPYING

%changelog
* Fri Nov 10 2006 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.1.beta4
Clean ups to submit FE.

* Tue Sep 19 2006 Yuichi Nakamura 2.0.1
Fixed policy for Cent OS4

* Mon Jul 3 2006 Yuichi Nakamura<himainu-ynakam@miomio.jp> 2.0.0
- Initial version
