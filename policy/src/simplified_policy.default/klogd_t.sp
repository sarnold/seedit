{
domain klogd_t;
program /sbin/klogd;

include common-relaxed.sp;
include daemon.sp;

allowpriv klog_adm;
allowpriv cap_sys_rawio;
allowpriv cap_sys_admin;
allow /dev/mem r,s;
allow /dev/kmem r,s;
allow /dev/console r,w,s;
allowfs proc_kmsg s,r;


}
