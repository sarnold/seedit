# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

{
domain sendmail_t;
program /usr/sbin/sendmail.sendmail;
include common-relaxed.sp;
include daemon.sp;
include logfile.sp;
include nameservice.sp;

allownet -protocol  tcp -port 25 server,client;
allownet -protocol  udp -port 512,53 client;


#utmp
allow initrc_var_run_t r,o,s;
allow /etc/mail/** r,s;
allow /var/spool/mail/** r,w,s;
allow /var/log/mail/** r,w,s;
allow /var/mail r,s;
allow /var/spool s;
allow /var/spool/mqueue/** r,w,s;
allow /var/spool/clientmqueue/** r,w,s; 
allow /etc/aliases.db r,w,s;
allow /etc/aliases r,w,s;
allow /root s;
allow etc_runtime_t r,s;
allow /usr/bin/procmail r,x,s;

allow system_crond_tmp_t r,s,a;

allowpriv netlink;
allowpriv cap_sys_tty_config;
#Add by seedit-generator
allowcom -ipc initrc_t w;
allow /etc/selinux/config  r,s;
allowpriv getsecurity;
}
