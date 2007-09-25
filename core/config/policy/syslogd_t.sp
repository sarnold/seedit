# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

{
domain syslogd_t;
program /sbin/syslogd, /sbin/minilogd;

include common-relaxed.sp;
include daemon.sp;
include nameservice.sp;

allowcom -unix login_t r,w;
allow /etc/syslog.conf r,s;
allow /var/log/* r,w,s;
allowtmp -dir /dev -name dev_log_t r,w,s;
allow /etc/selinux/config r;
}
