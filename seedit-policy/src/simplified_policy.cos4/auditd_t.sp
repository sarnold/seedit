{
domain auditd_t;
program /sbin/auditd;

include common-relaxed.sp;
include daemon.sp;
include nameservice.sp;

allowpriv cap_sys_nice;
allowpriv netlink;
allowpriv cap_sys_resource;
allowpriv netlink;
allowpriv audit_adm;

allow /var/log/audit/**  r,a,c,s;
allow /etc/audit.rules r,s;
allow /etc/auditd.conf r,s;

allowfs proc_pid_self  w;

}
