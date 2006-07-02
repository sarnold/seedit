%define type strict
%define selinuxconf /etc/selinux/config
%define distro COS4
Summary: Simplified Policy for SELinux
#Name: seedit-policy-%{type}
Name: seedit-policy
Version: 2.0.0.rc1
Release: %{distro}.4
License: GPL
Group:  System Environment/Base
URL:  http://seedit.sourceforge.net/
Source0: seedit-policy-%{version}.tar.gz
BuildRoot: %{_tmppath}/seedit-policy-%{version}-%{release}-root
BuildArch: noarch
Requires: seedit-converter >= 2.0.0, checkpolicy,m4,audit
BuildRequires: seedit-converter >= 2.0.0

%description
Simplified policy for SELinux is packed.
Simplified policy is converted into usual SELinux policy by seedit-converter.

%prep
%setup -q -n seedit-policy-%{version}

%build

%install
rm -rf $RPM_BUILD_ROOT
DISTRO=%{distro}
%makeinstall CONVERTER=/usr/bin/seedit-converter DISTRO=$DISTRO POLICYTYPE=%{type} DEVELFLAG=0 SELINUXTYPE=seedit

%pre
if [ -e /etc/selinux/seedit/contexts/files/file_contexts.all.old ] ; then
	cp /etc/selinux/seedit/contexts/files/file_contexts.all.old /etc/selinux/seedit/contexts/files/file_contexts.all.old2
fi

%post
if [ $1 = 1 ]; then
	cat %{selinuxconf} |sed -e 's/^SELINUX=.*$/SELINUX=permissive/'|sed -e 's/^SELINUXTYPE=.*$/SELINUXTYPE=seedit/' >%{selinuxconf}.tmp
	mv %{selinuxconf} %{selinuxconf}.orig
	mv  %{selinuxconf}.tmp %{selinuxconf}
	touch /.autorelabel

	echo "/var/tmp/bootstrap.sh" >> /etc/rc.d/rc.local

	# Create bootstrap.sh # Code related to bootstrap is from Yoichi Hirose <yhirose@users.sourceforge.jp>
	cat << __EOF >/var/tmp/bootstrap.sh

#!/bin/sh
/usr/sbin/seedit-restorecon -R /etc -v
/usr/sbin/seedit-load -v
cat /etc/rc.d/rc.local | sed -e 's!/var/tmp/bootstrap.sh!!g' > /etc/rc.d/rc.local.tmp
rm -f /etc/rc.d/rc.local
mv /etc/rc.d/rc.local.tmp /etc/rc.d/rc.local
chmod 0755 /etc/rc.d/rc.local
init 6

__EOF
	chmod 755 /var/tmp/bootstrap.sh
	/sbin/chkconfig auditd on

fi

if [ -e /etc/seedit/policy/sysadm_r.sp ]; then
	/usr/sbin/seedit-rbac off -n
fi

%postun
if [ $1 = 0 ]; then
	cat %{selinuxconf} |sed -e 's/^SELINUX=.*$/SELINUX=permissive/'|sed -e 's/^SELINUXTYPE=.*$/SELINUXTYPE=targeted/' >%{selinuxconf}.tmp
	mv %{selinuxconf} %{selinuxconf}.orig
	mv %{selinuxconf}.tmp %{selinuxconf}
	touch /.autorelabel

else
	mv /etc/selinux/seedit/contexts/files/file_contexts.all.old2 /etc/selinux/seedit/contexts/files/file_contexts.all.old
	if [ -e /etc/seedit/policy/sysadm_r.sp ]; then
		/usr/sbin/seedit-rbac on -n
	fi
	/usr/sbin/seedit-load -v
fi


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
/etc/selinux/seedit
/etc/seedit
%config /etc/seedit/policy

%changelog
* Sat Jul 1 2006 Yuichi Nakamura<himainu-ynakam@miomio.jp> 2.0.0
- Initial version
