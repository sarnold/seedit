{
domain mcstransd_t;
program /sbin/mcstransd;
include common-relaxed.sp;
include daemon.sp;
include logfile.sp;
include nameservice.sp;

#Add by seedit-generator
allowfs proc_pid_other  r,s;
allowpriv getsecattr;
allow /var/run/setrans/** w,r,s;
allowpriv cap_sys_resource;
allowpriv getsecurity;
#Add by seedit-generator
allow /etc/selinux/** r,s;
}
