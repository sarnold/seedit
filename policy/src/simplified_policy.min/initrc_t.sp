# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

{
domain initrc_t;
domain_trans kernel_t /etc/init.d, /etc/rc.d/rc,/etc/rc.d/rc.sysinit,/etc/rc.d/rc.local;
domain_trans unconfined_t /etc/rc.d/init.d, /etc/init.d;
include common-relaxed.sp;
include daemon.sp;

allowtmp -dir /etc -name etc_runtime_t;
allowpriv all;
}
