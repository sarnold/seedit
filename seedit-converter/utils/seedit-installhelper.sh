#!/bin/sh
# Helper to install/uninstall seedit
SELINUXCONF=/etc/selinux/config
AUDITRULES=/etc/audit/audit.rules
MODULAR=n

install_seedit() {

	cat $SELINUXCONF |sed -e 's/^SELINUX=.*$/SELINUX=permissive/'|sed -e 's/^SELINUXTYPE=.*$/SELINUXTYPE=seedit/' >$SELINUXCONF.tmp
	mv $SELINUXCONF $SELINUXCONF.orig
	mv  $SELINUXCONF.tmp $SELINUXCONF
	touch /.autorelabel

	echo "/var/tmp/bootstrap.sh" >> /etc/rc.d/rc.local
	if [ -e $AUDITRULES ]; then
	        cat $AUDITRULES | sed -e 's!-a exit,always -S chroot!!g' > $AUDITRULES.tmp
		mv $AUDITRULES.tmp $AUDITRULES
	 			
		echo "-a exit,always -S chroot" >> $AUDITRULES
	fi
	if [ -e /etc/selinux/restorecond.conf ];then 
		cat /etc/selinux/restorecond.conf |sed -e 's/^\/etc\/ld.so.cache.*$//'>/etc/selinux/restorecond.conf.tmp
		cp /etc/selinux/restorecond.conf.tmp /etc/selinux/restorecond.conf
	fi
	echo "/etc/ld.so.cache" >> /etc/selinux/restorecond.conf
	
	if [ $MODULAR = "y" ]; then
		/usr/sbin/semodule -b /usr/share/seedit/sepolicy/base.pp -s seedit -n
	fi

	# Create bootstrap.sh # Code related to bootstrap is from Yoichi Hirose <yhirose@users.sourceforge.jp>
	cat << __EOF >/var/tmp/bootstrap.sh

#!/bin/sh
/usr/sbin/seedit-restorecon -R /etc -v
/usr/sbin/seedit-load -v
cat /etc/rc.d/rc.local | sed -e 's!/var/tmp/bootstrap.sh!!g' > /etc/rc.d/rc.local.tmp
rm -f /etc/rc.d/rc.local
mv /etc/rc.d/rc.local.tmp /etc/rc.d/rc.local
/usr/sbin/seedit-restorecon  /etc/rc.d/rc.local -v
chmod 0755 /etc/rc.d/rc.local
init 6

__EOF

	chmod 755 /var/tmp/bootstrap.sh
	/sbin/chkconfig auditd on
}

uninstall_seedit() {

	cat $SELINUXCONF |sed -e 's/^SELINUX=.*$/SELINUX=permissive/'|sed -e 's/^SELINUXTYPE=.*$/SELINUXTYPE=targeted/' >$SELINUXCONF.tmp
	mv $SELINUXCONF $SELINUXCONF.orig
	mv $SELINUXCONF.tmp $SELINUXCONF
	touch /.autorelabel
	if [ -e $AUDITRULES ]; then
	        cat $AUDITRULES | sed -e 's!-a exit,always -S chroot!!g' > $AUDITRULES.tmp
		mv $AUDITRULES.tmp $AUDITRULES
	fi

}

if [ $1 = "install" ]; then
    install_seedit
fi


if [ $1 = "uninstall" ]; then
    uninstall_seedit
fi
