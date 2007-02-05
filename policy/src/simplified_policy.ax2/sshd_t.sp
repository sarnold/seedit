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
allowpriv cap_chown;
allowpriv cap_dac_override;
allowpriv cap_dac_read_search;
allowpriv cap_sys_tty_config;

allowpriv getsecurity;
allowpriv setsecurity;

allow /etc/selinux/** r,s;
allow /root/** s;
allow ~/** s;
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

#utmp
allow initrc_var_run_t  r,o,s;

allowfs proc_pid_self r,w,s;
allowpriv netlink;
allowpriv audit_write;
}
