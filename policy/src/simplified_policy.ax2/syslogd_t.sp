{
domain syslogd_t;
program /sbin/syslogd, /sbin/minilogd;

include common-relaxed.sp;
include daemon.sp;
include nameservice.sp;

allowcom -unix login_t r,w;
allow /etc/syslog.conf r,s;
allow /var/log/* r,w,s;
allow /var/log/rflogview/** r,w,s;
allowtmp -dir /dev -name dev_log_t r,w,s;
}
