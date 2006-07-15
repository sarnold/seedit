#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

{
domain named_t;
program /usr/sbin/named;
include common-relaxed.sp;
include daemon.sp;
include nameservice.sp;

allow /usr/sbin/named  r,s,x;
allow /var/named/** r,s;

allow /var/named/chroot/var/run/named/* r,w,s;
allowdev -root /var/named/chroot/dev;
allow /var/named/chroot/dev/* r,w,s;
allow /etc/named.conf r;
allow /etc/named.caching-nameserver.conf r;
allow /etc/named.rfc1912.zones r;
allow /etc/rndc.key r;
allow /var/run/named/* r,w,s;

allownet -protocol udp -port 53 server;
allownet -protocol tcp -port 53,953 server;
allowpriv cap_sys_chroot;

}
