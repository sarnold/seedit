{
domain newrole_t;
domain_trans sysadm_r,user_r,staff_r /usr/bin/newrole;
include common-relaxed.sp;

allowdev -allterm all admin;

allow /var/log r,w,s;
allow /etc/selinux/seedit r,s;
allow /etc/shadow r,s;
allow /dev/console r,w,s;

allowfs proc_pid_self w;
allowpriv netlink;
allowpriv audit_write;
allowpriv getsecurity;
}
