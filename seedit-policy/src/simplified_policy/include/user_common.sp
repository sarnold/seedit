domain_trans sshd_t,newrole_t,login_t,su_t /bin/bash,/bin/sh;
domain_trans gdm_t /etc/X11/xdm/Xsession;


allowdev -tty open;
allowdev -pts open;

allow ~/** r,w,x,s;
allow /etc/passwd r,s;
allow /bin/bash r,x,s;
allow /bin/sh r,s;
allow /bin/** r,x,s;
allow /usr/bin/** r,x,s;
allow etc_runtime_t r,s;

allownet -protocol tcp,udp -port * client;

allowtmp -dir /tmp -name auto r,w,s;
allowtmp -fs tmpfs -name auto r,w,s;
