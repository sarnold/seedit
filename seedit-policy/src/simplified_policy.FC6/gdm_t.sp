# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

{
domain gdm_t;
domain_trans init_t /usr/bin/gdm-binary,/usr/sbin/gdm-binary;
domain_trans init_t /usr/bin/gdmgreeter,/usr/sbin/gdmgreeter;
domain_trans init_t /usr/bin/kdm,/usr/bin/kdm_greet;
include common-relaxed.sp;
include tmpfile.sp;

allow /usr/bin/Xorg r,dx;
allowtmp -dir ~/ -name xauthority_t r,w,s;
allowpriv all;
}
