#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

{
domain ntpd_t;
program /usr/sbin/ntpd;
include common-relaxed.sp;
include daemon.sp;
include nameservice.sp;

allowpriv cap_ipc_lock;
allowpriv cap_sys_time;
allowpriv cap_sys_resource;
allowpriv netlink;

allow /etc/ntp.conf r,s;
allow /etc/ntp/** r,s;
allow /var/lib/ntp/** r,w,s;

allownet -protocol udp,tcp -port 123 client,server;
allownet -protocol  udp -port 53 client;

allow etc_runtime_t r,s;
}
