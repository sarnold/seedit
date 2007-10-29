# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

{
domain syslogd_t;
program /sbin/syslogd, /sbin/minilogd, /sbin/rsyslogd;

include common-relaxed.sp;
include daemon.sp;
include nameservice.sp;

allowcom -unix login_t r,w;
allow /etc/rsyslog.conf r,s;
allow /var/log/* r,w,s;
allowtmp -dir /dev -name devlog_t r,w,s;
}
