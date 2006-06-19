#Common Access rights for daemons

allow dev_log_t r,w,s;
allowcom -unix syslogd_t r,w;
allowtmp -dir /var/run -name auto r,w,s;

allow /var/log s;
allow /var/run/** s;
allow /etc/localtime s,r;
allow /etc/nsswitch.conf s,r;
allow /etc/protocols s,r;
allow /etc/resolv.conf r,s;
allow /etc/environment r,s;
allow /etc/hosts.allow r,s;
allow /etc/hosts.deny r,s;
#Protect tmp file
include tmpfile.sp

#To change  from uid=0 
#And it is not audited in permissive mode, 
allowpriv cap_setuid;
allowpriv cap_setgid;
