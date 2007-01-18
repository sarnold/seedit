allowtmp -dir /tmp -name auto r,w,s;
allowtmp -dir /var/tmp -name auto r,w,s;
allowtmp -fs tmpfs -name auto r,w,s;
allow /usr/tmp  r,s;
