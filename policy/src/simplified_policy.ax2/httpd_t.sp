#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

{
domain httpd_t;
program /usr/sbin/httpd;
include common-relaxed.sp;
include daemon.sp;
include nameservice.sp;

allow /etc/httpd/** r,s;
allow etc_runtime_t r,s;
allow /var/log/httpd/** r,a,s,c;
allow /var/www/** r,s;
allow /var/run/** s;
allow /etc/php.d/** r,s;
allow /etc/php.ini r,s;
allow /etc/mime.types r,s;
allow /etc/pki/** r,s;
allow ~/public_html/** r,s;
allow /usr/share/file/** r,s;

allow /usr/bin/* r,s,x;
allow /var/www/cgi-bin/** r,x,s;

allownet -protocol tcp -port 80,443 server;

allowpriv netlink;
#Add by seedit-generator
allow /etc/krb5.conf  w,r,s;
allow /usr/share/snmp/mibs/** w,r,s;
allow /etc/snmp/** s,r;
}
