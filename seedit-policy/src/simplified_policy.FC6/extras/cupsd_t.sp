{
domain cupsd_t;
program /usr/sbin/cupsd;
include common-relaxed.sp;
include daemon.sp;
include logfile.sp;
include nameservice.sp;

#Write access control here....

#Add by seedit-generator
allownet -protocol udp -port 631 server;
allow /var/run/cups/** w,r,s;
allow /var/log/cups/** r,s,c,a,t;
allowpriv cap_fsetid;
allow /etc/cups/** r,s;
allow /usr/share/cups/** r,s;
allownet -protocol tcp -port 631 server;
allowpriv netlink;
allowpriv cap_dac_override;
allow /etc/printcap  o,r,s;
#Add by seedit-generator
allow /var/cache/cups/** w,r,s;
#Add by seedit-generator
allow /root  s;
allow /var/spool/cups/** r,w,s;
#Add by seedit-generator
allowpriv cap_chown;
}
