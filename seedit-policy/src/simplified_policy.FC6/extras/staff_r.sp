# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

{
role staff_r;
user root;

include user_common.sp;
include common-relaxed.sp;

allow /root/** r,w,s;
allow ~/** r,w,s;

}
