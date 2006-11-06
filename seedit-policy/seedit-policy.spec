%define selinuxconf /etc/selinux/config
%define auditrules  /etc/audit/audit.rules
%define installhelper /usr/share/seedit/scripts/seedit-installhelper.sh
%define distro FC6
%define modular y
%define buildnum 1
Summary: Simplified Policy for SELinux
Name: seedit-policy
Version: 2.1.0.b4
Release: %{buildnum}.%{distro}
License: GPL
Group:  System Environment/Base
URL:  http://seedit.sourceforge.net/
Source0: seedit-policy-%{version}-%{buildnum}.tar.gz
BuildRoot: %{_tmppath}/seedit-policy-%{version}-%{release}-root
BuildArch: noarch
Requires: seedit-converter >= 2.1.0, checkpolicy,m4,audit
BuildRequires: seedit-converter >= 2.1.0,checkpolicy,m4

%description
Simplified policy for SELinux is packed.
Simplified policy is converted into usual SELinux policy by seedit-converter.

%prep
%setup -q -n seedit-policy-%{version}

%build

%install
rm -rf $RPM_BUILD_ROOT
DISTRO=%{distro}
%makeinstall CONVERTER=/usr/bin/seedit-converter DISTRO=$DISTRO  DEVELFLAG=0 SELINUXTYPE=seedit

%pre
if [ -e /etc/selinux/seedit/contexts/files/file_contexts.all.old ] ; then
	cp /etc/selinux/seedit/contexts/files/file_contexts.all.old /etc/selinux/seedit/contexts/files/file_contexts.all.old2
fi

%post
export SELINUXCONF=%{selinuxconf}
export AUDITRULES=%{auditrules}
if [ $1 = 1 ]; then	
	%{installhelper} install
fi

if [ -e /etc/seedit/policy/sysadm_r.sp ]; then
	/usr/sbin/seedit-rbac off -n
	touch /etc/seedit/policy/rbac_flag
fi

%postun
export SELINUXCONF=%{selinuxconf}
export AUDITRULES=%{auditrules}

if [ $1 = 0 ]; then
	%{installhelper} uninstall

else
	mv /etc/selinux/seedit/contexts/files/file_contexts.all.old2 /etc/selinux/seedit/contexts/files/file_contexts.all.old
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
/etc/selinux/seedit
%config /etc/seedit/policy
/usr/share/seedit/sepolicy
%doc README
%doc Changelog
%doc COPYING

%changelog
* Tue Sep 19 2006 Yuichi Nakamura 2.0.1
Fixed policy for Cent OS4

* Mon Jul 3 2006 Yuichi Nakamura<himainu-ynakam@miomio.jp> 2.0.0
- Initial version
