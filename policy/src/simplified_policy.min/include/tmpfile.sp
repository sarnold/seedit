# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

allowtmp -dir /tmp -name auto r,w,s;
allowtmp -dir /var/tmp -name auto r,w,s;
allowtmp -fs tmpfs -name auto r,w,s;
