# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

domain_trans sshd_t,newrole_t,login_t /bin/bash,/bin/sh;
domain_trans gdm_t /etc/X11/xdm/Xsession;


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

allowcom -ipc unix r,w;
