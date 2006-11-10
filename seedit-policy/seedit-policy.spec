%define distro FC6
%define betatag beta4
%define buildnum 1

%define selinuxconf /etc/selinux/config
%define auditrules  /etc/audit/audit.rules
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
BuildRequires: seedit-converter >= 2.1.0,checkpolicy,m4

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
make install DESTDIR="%{buildroot}" CONVERTER=/usr/bin/seedit-converter DISTRO=$DISTRO  DEVELFLAG=0 SELINUXTYPE=seedit MODULAR=$MODULAR

%pre
if [ $2 = 2 ]; then
	# If rbac is enabled in upgrade, should be disabled temporally
	# After uninstall of previous package, enabled. 
	if [ -e /etc/seedit/policy/sysadm_r.sp ]; then
		/usr/sbin/seedit-rbac off -n
		touch /etc/seedit/policy/rbac_flag
	fi
fi

%post
if [ $1 = 1 ]; then
	#Setup /etc/selinux/config, automatic relabel, initialization at boot
	export SELINUXCONF=%{selinuxconf}
	export AUDITRULES=%{auditrules}
	export MODULAR=%{modular}
	%{installhelper} install
fi


%preun

if [ $1 = 0 ]; then
	export SELINUXCONF=%{selinuxconf}
	export AUDITRULES=%{auditrules}
	export MODULAR=%{modular}
	#Go back to targeted policy, automatic relabel
	%{installhelper} uninstall
fi

if [ $1 = 2 ]; then 
	#If RBAC is disabled temporally at upgrade, enable it again
	if [ -e /etc/seedit/policy/rbac_flag ]; then
		/usr/sbin/seedit-rbac on -n
		rm /etc/seedit/policy/rbac_flag
	fi
	/usr/sbin/seedit-load -v
fi


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%config(noreplace) /etc/selinux/seedit
%config(noreplace) /etc/seedit/policy
/usr/share/seedit/sepolicy
/usr/share/seedit/scripts
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
