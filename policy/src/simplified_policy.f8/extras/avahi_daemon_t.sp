{
domain avahi_daemon_t;
program /usr/sbin/avahi-daemon;
include common-relaxed.sp;
include daemon.sp;
include logfile.sp;
include nameservice.sp;

#Write access control here....

#Add by seedit-generator
allow /var/run/dbus/system_bus_socket  w,r,s;
allownet -protocol udp -port 1024- client;
allow /var/run/avahi-daemon/** r,s;
allowpriv cap_sys_chroot;
allownet -protocol udp -port 5353 server;
allow /etc/avahi/** r,s;
allow /var/run/avahi-daemon/** w,r,s;
allow /var/run/dbus/** o,r,s,t;
allowpriv netlink;
allowpriv cap_chown;
allowcom -ipc initrc_t w;
allow /var/run/avahi-daemon/** w,r,s;
#Add by seedit-generator
allowpriv cap_dac_override;
}
