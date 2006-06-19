{
domain firefox_t;
program /usr/bin/firefox;
include common-relaxed.sp;
include tmpfile.sp;
include nameservice.sp;
include xapps.sp;


#get some SELinux infomation
allow /etc/selinux/config  r,s;
allowpriv getsecurity;

allowcom -ipc unconfined_t w,r;
allowcom -ipc xserver_t r,w;

#access to system files
allow /etc/localtime  r,s;
allow /etc/rc.d/init.d  s;
allow /usr/share/doc/HTML/** r,s;
allow /var/run/nscd/**  r,s;
allowfs proc_pid_other  o,r,s;
allowfs inotifyfs  r,s;
allow /etc/init.d r,s;

#access to commands
allow /bin/** x,r,s;
allow /usr/bin/** x,r,s;

#access to other process's tmp files
allow gdm_tmp_t  o,r,s;
allow unconfined_tmp_t  r,w,s;
allow xauthority_t  r,s;


allowpriv netlink;

allownet -protocol tcp -port 80,443 client;
allownet -protocol tcp -port 1024- client;

#access to home dirs
allow ~/** r,w,s;
deny ~/Desktop/** ;
allow ~/.mozilla/** r,w,s;
allow ~/.local/**  s,r;


}
