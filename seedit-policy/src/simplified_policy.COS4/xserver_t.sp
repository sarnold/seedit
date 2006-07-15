#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

{
domain xserver_t;
program /usr/bin/Xorg;
include common-relaxed.sp;
include tmpfile.sp;

allowpriv all;
}
