#

allow /etc/group r,s;
allow /etc/host.conf r,s;
allow /etc/hosts r,s;
allow /etc/nsswitch.conf r,s;
allow /etc/passwd r,s;
allow /etc/protocols r,s;
allow /etc/resolv.conf r,s;
allow /etc/services r,s;

allownet -protocol udp -port 53 client;
