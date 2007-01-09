#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

{
domain su_t;
domain_trans staff_r,sysadm_r /bin/su;
include common-relaxed.sp;
include authentication.sp;
include nameservice.sp;

allow /root s;
allow /etc/** r,s;

allow /bin/bash r,x;
allow /bin/sh r,s;
allowpriv all;

allowpriv getsecurity;
allowpriv netlink;
allowpriv audit_write;
allowdev -allterm all admin;
allowfs proc_pid_self  s,r,w;
allowcom -sig user_r c;
allowcom -sig staff_r c;
allowcom -sig sysadm_r c;
}
