#Access rights to do authentication
#Many critical files are read!

allow /etc/pam.d/** r,s;
allow /etc/security/** r,s;
allow /etc/shadow r,s;
allow /etc/gshadow r,s;


