{
domain sshd_t;
program /usr/sbin/sshd ;

include common-relaxed.sp;
include nameservice.sp;
include authentication.sp;
include daemon.sp;

allownet -protocol tcp -port 22 server;

allowdev -pts all r,w;
allowdev -pts all admin;
allowdev -pts general admin;
allowdev -pts open;

allowpriv cap_sys_chroot;
allowpriv getsecurity;

allow /etc/selinux/** r,s;
allow /root/** s;
allow /home/** s;
allow /etc/ssh/** r,s;
allow /etc/krb5.conf r,o,s;
allow /etc/security/** r,s;
allow /etc/hosts.allow r,s;
allow /etc/hosts.deny r,s;
allow etc_runtime_t r,s;
allow /usr/sbin/sshd r,s,x;
allow /bin/bash r,x;

allow /var/empty/** r,s;
allow /var/log/* r,w,s;

# for FC5
allow /var/run/nscd/* r,s;
#utmp
allow initrc_var_run_t  r,o,s;

allowfs proc_pid_self r,w,s;
allowpriv netlink;
allowpriv audit_write;
}