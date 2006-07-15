#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

{
domain newrole_t;
domain_trans sysadm_r,user_r,staff_r /usr/bin/newrole;
include common-relaxed.sp;
include authentication.sp;
include nameservice.sp;

allowdev -allterm all admin;

allow /etc/selinux/** r,s;
allow /dev/console r,w,s;
allow /bin/bash r,x;
allow /bin/sh r;
allow initrc_var_run_t r,o,t;
allow /var/run/** r,s;
allow /etc/** r,s;
allow /sbin/** r,x,s;
allow /dev/full r,o,t,s;

allowfs proc_pid_self w;
allowpriv netlink;
allowpriv audit_write;
allowpriv getsecurity;
allowpriv setsecurity;

allowcom -ipc syslogd_t r,w;
allow dev_log_t r,o,t;

}
