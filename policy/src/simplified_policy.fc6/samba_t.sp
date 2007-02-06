{
domain samba_t;
program /usr/sbin/smbd,/usr/sbin/nmbd;
include common-relaxed.sp;
include daemon.sp;
include nameservice.sp;

allow /var/log/samba/** r,a,c,s;
allow /var/cache/samba/** r,w,s;
allow /etc/printcap r,s;

#if you have restorecond, add /etc/secrets.tdb,smbpasswd and remove following 
allow /etc/samba/** r,s,t;
allowtmp -dir /etc/samba -name auto r,w,s;


#Full access to user home directories. If you do not want to allow, fix here 
allow ~/** r,w,s;


allowpriv cap_sys_resource;

allownet -protocol udp -port 137,138 client;
allownet -protocol udp -port 137,138 server;
allownet -protocol tcp -port 445,139 server;

#Add by seedit-generator
allow /etc/cups/** r,s;
}
