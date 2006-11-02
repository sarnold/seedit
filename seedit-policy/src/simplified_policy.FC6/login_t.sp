# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

{
domain login_t;
domain_trans init_t /bin/login;
include common-relaxed.sp;

allowpriv all;
}
