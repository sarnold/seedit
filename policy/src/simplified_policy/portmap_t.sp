#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

{
domain portmap_t;
program /sbin/portmap;
include common-relaxed.sp;
include daemon.sp;
include nameservice.sp;

allownet -protocol tcp,udp -port -1023 server;
allownet -protocol tcp,udp -port * client;

}
