#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

{
domain auditd_t;
program /sbin/auditd;

include common-relaxed.sp;
include daemon.sp;
include nameservice.sp;

allowpriv cap_sys_nice;
allowpriv netlink;
allowpriv cap_sys_resource;
allowpriv netlink;
allowpriv audit_adm;

allow /var/log/audit/**  r,a,c,s;
allow /etc/audit/** r,s;
allow /sbin/audispd r,x,s;

allowfs proc_pid_self  w;

#Add by seedit-generator
allow /usr/bin/** x,r,s;
allow /bin/** x,r,s;
}
