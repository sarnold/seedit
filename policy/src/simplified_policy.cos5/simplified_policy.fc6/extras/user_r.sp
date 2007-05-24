# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

{
role user_r;
user user_u;

include user_common.sp;
include common-relaxed.sp

allow ~/** r,w,s;
}
