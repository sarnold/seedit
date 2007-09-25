# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

{
domain unconfined_t;
program /bin/login;
include common-relaxed.sp;
include daemon.sp;

allowpriv all;
}
