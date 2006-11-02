# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

{
#comment: domain for rpm. Do not use this domain from other than sysadm_r.
domain rpm_t;
program /bin/rpm,/usr/bin/yum;
include common-relaxed.sp;

allowpriv all;
}
