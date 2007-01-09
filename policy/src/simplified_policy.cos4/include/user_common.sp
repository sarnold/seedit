include local_login.sp

allowdev -tty open;
allowdev -pts open;
allow /etc/passwd r,s;
allow /bin/bash r,x,s;
allow /bin/sh r,s;
allow /bin/** r,x,s;
allow /usr/bin/** r,x,s;
allow /usr/sbin/** r,x,s;
allow /sbin/** r,x,s;
allow etc_runtime_t r,s;
allow /etc/** r,s;
allow /etc/profile.d/** r,x,s;
allow /usr/share/** r,s;
allow /etc/sysconfig/* r,s;
allow /var/spool/mail/** r,s;
allow  /var/run/nscd/** r,s;

allownet -protocol tcp,udp -port * client;

allowtmp -dir /tmp -name auto r,w,s;
allowtmp -fs tmpfs -name auto r,w,s;

allow /usr/libexec/openssh/** r,x,s;

allowpriv getsecurity;
allowpriv setsecurity;
allowpriv cap_chown;
allowpriv cap_sys_tty_config;

allowcom -ipc self r,w;
