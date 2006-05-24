{
domain unconfined_t;
domain_trans login_t, sshd_t,unconfined_su_t /bin/bash,/bin/sh;
domain_trans gdm_t /etc/X11/xdm/Xsession;
include common-relaxed.sp;
include daemon.sp;

allowpriv all;
}
