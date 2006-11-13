%define distro COS4
%define buildnum 1
%define betatag beta4

%define python_ver 2.3
%define pam_include_support n

Summary: GUI for SELinux Policy Editor
Name: seedit-gui
Version: 2.1.0
Release:  0.%{buildnum}.%{betatag}.%{distro}
License: GPL
Group: System Environment/Base
URL: http://sedit.sourceforge.net/
Source0: %{name}-%{version}-%{betatag}.tar.gz
Source1: seedit-gui.desktop
Source2: seedit-gui.png
BuildRoot: %{_tmppath}/%{name}-%{version}-%{betatag}-root-%(%{__id_u} -n)
BuildArch: noarch
Requires: seedit-converter >= 2.1.0, seedit-policy >= 2.1.0,audit,pygtk2

%description
X Window based GUI for SELinux Policy Editor

%prep
%setup -q

%build
make clean
make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR="%{buildroot}" PYTHON_VER=%{python_ver} DISTRO=%{distro} PAM_INCLUDE_SUPPORT=%{pam_include_support}

install -d -m 755 ${RPM_BUILD_ROOT}%{_datadir}/applications
install -m 664 %{SOURCE1} ${RPM_BUILD_ROOT}%{_datadir}/applications/seedit-gui.desktop
mkdir -p $RPM_BUILD_ROOT/usr/share/pixmaps
install -m 664 %{SOURCE2} ${RPM_BUILD_ROOT}/usr/share/pixmaps/seedit-gui.png


%find_lang %{name}


%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(-,root,root,-)
%{_bindir}/seedit-gui
%{_sbindir}/seedit-gui
%{_sbindir}/seedit-gui-status
%{_sbindir}/seedit-gui-domain-manager
%{_sbindir}/seedit-gui-role-manager
%{_sbindir}/seedit-gui-generate-policy
%{_sbindir}/seedit-gui-edit
%{_sbindir}/seedit-gui-load
%{_libdir}/python%{python_ver}/site-packages/seedit/ui
/usr/share/icons/seedit
/usr/share/applications/seedit-gui.desktop
%config(noreplace) /etc/security/console.apps/seedit-gui
%config(noreplace) /etc/pam.d/seedit-gui
/usr/share/pixmaps/seedit-gui.png
%doc README
%doc Changelog
%doc COPYING

%changelog
* Fri Nov 10 2006 Yuichi Nakamura<ynakam@hitachisoft.jp> 2.1.0-0.1.beta4
 Clean ups to submit FE.
 Merged icons from Shane M. Coughlan.

* Tue Sep 26 2006 Yuichi Nakamura 2.0.2
Merged changes(about lanugage changes) from Shane M. Coughlan.

* Tue Sep 19 2006 Yuichi Nakamura 2.0.1
Fixed bug for Cent OS 4
Merged clean up about copyright statement from Shane M. Coughlan.

* Mon Jul 3 2006 Yuichi Nakamura<himainu-ynakam@miomio.jp> 2.0.0
- Initial version

