{
domain su_t;
domain_trans staff_r,sysadm_r /bin/su;
include common-relaxed.sp;
allow /etc/shadow r,s;
allow /root s;
allow /etc/selinux/seedit/** r,s;

allowpriv getsecurity;
allowpriv netlink;
allowpriv audit_write;
allowdev -allterm all admin;
allowfs proc_pid_self  s,r,w;
allowcom -sig user_r c;
allowcom -sig staff_r c;
allowcom -sig sysadm_r c;
}
