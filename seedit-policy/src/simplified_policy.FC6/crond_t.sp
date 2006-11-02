# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

{
domain crond_t;
program /usr/sbin/crond,/usr/sbin/atd ;

include common-relaxed.sp;
include daemon.sp;
include authentication.sp;
include nameservice.sp;

allow /etc/selinux/** r,s;
allow /etc/crontab r,x,s;
allow /etc/cron.daily/** r,s,x;
allow /etc/cron.hourly/** r,s,x;
allow /etc/cron.weekly/** r,s,x;
allow /etc/cron.monthly/** r,s,x;
allow /var/spool s;
allow /var/spool/cron/** r,s,x;
allow /var/spool/at/** r,s,x;
allow /var/spool/anacron r,s,w;
allow /etc/cron.d/** r,s;
allow /var/log/* r,w,s;
allow /bin/sh r,s;
allow /bin/bash r,x,s;

#to get selinux security information
allowpriv getsecurity;
allowpriv setsecurity;

allowfs proc_pid_self r,w,s;
allowpriv netlink;
allowpriv audit_write;

allowpriv cap_dac_override;
allowpriv cap_dac_read_search;
#Add by seedit-generator
allowcom -ipc initrc_t w;
allow /var/run/setrans/** o,r,s;

allowkey kernel_t l,s ;
}
