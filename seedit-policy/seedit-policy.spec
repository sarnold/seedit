%define type strict
%define selinuxconf /etc/selinux/config
%define distro FC5
Summary: Sample policy of Simplified Policy
#Name: seedit-policy-%{type}
Name: seedit-policy
Version: 2.0.0.b7
Release: %{distro}
License: GPL
Group:  System Environment/Base
URL:  http://seedit.sourceforge.net/
Source0: seedit-policy-%{version}.tar.gz
BuildRoot: %{_tmppath}/seedit-policy-%{version}-%{release}-root
BuildArch: noarch
Requires: seedit-converter >= 2.0.0, checkpolicy,m4
BuildRequires: seedit-converter >= 2.0.0

%description

%package devel
Summary: Sample policy of Simplified Policy for developpers. 
Group: System Environment/Base
Requires: seedit-converter

%description devel
Sample policy of Simplified Policy for developpers. It contains configuration using macros in template_macros.te

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
* Tue Apr 18 2006 Yuichi Nakamura <ynakam@gwu.edu>
1.4.0-test1
* Wed Feb 27 2006 Yuichi Nakmaura <ynakam@gwu.edu>
1.3.3
* Wed Feb 1 2006 Yuichi Nakmaura <ynakam@gwu.edu>
Small fix for XML support
* Tue Jan 17 2006 Yuichi Nakamura <ynakam@gwu.edu>
1.3.1 fix spdl_spec.xml to eleminate permission overlap
* Fri Jan 13 2006 Yuichi Nakamura <ynakam@gwu.edu>
1.3 
* Tue Aug 23 2005 Yuichi Nakamura <ynakam@gwu.edu>
1.2
add devel package
* Wed Jul 20 2005  Yuichi Nakamura <ynakam@gwu.edu> 
1.1
Add policy for X, cron.
* Sun Jul 13 2005  Yuichi Nakamura <ynakam@gwu.edu> 
1.0
- Initial build.

