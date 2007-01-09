#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

{
role sysadm_r;
user root;
include user_common.sp;

allowpriv all;
}
