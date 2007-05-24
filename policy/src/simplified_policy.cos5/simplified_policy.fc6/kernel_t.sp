# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

{
domain kernel_t;
include common-relaxed.sp;

allowpriv all;
}
