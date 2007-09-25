# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

#common configuration common to all domain
#This should be included first

allowdev -root /dev;

allow /* s;

allow /dev/console s,r,w;
allow /dev/null s,r,w;
allow /dev/zero s,r,w;
allow /dev/random s,r,w;
allow /dev/urandom s,r,x;

# allow communication within domain
allowcom -ipc self r,w;
allowcom -sig init_t c;
allowcom -sig self c,k,s,o,n;

#/proc/pid
allowfs proc_pid_self r,s;

# read only access to some misc file systems
allowfs proc r,s;
allowfs usbfs r,s;
allowfs sysfs r,s;

# everyone can read/write tty/pts, but can not create
allowdev -allterm general r,w;
allowdev -allterm all r,w;

allow /bin/** s;
allow /usr/** s;
allow /sbin/** s;

#shared lib
allow /usr/lib/** r,x,s;
allow /lib/** r,x,s;
allow ldconfig_cache_t s,r;

# to prevent misconfiguration
deny /etc/shadow;
deny /etc/shadow-;
deny /dev;
deny /dev/kmem;
deny /dev/mem;
deny /dev/port;
deny /var/log;

allow /usr/share/locale/** r,s;

#skip permission check in NIC and node layer
allownet -protocol * -netif * send,recv;
allownet -protocol * -node * send,recv,bind;

allowkey self *;
