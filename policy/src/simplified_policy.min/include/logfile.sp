# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

#can create and append logfile under /var/log
allowtmp -dir /var/log -name auto s,r,a,t,c;
