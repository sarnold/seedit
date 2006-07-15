#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

{
domain unconfined_restorecon_t;
program /sbin/restorecon;
include common-relaxed.sp;

allowpriv all;
}
