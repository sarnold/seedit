# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

{
domain init_t;
domain_trans kernel_t /sbin/init;
include common-relaxed.sp;

allowpriv all;
allowtmp -dir /etc -name etc_runtime_t;
}
