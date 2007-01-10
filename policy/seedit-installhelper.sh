#!/bin/sh
# Helper to install/uninstall seedit
#define below
#SELINUXCONF=/etc/selinux/config
#AUDITRULES=/etc/audit/audit.rules
#MODULAR=n
. /usr/share/seedit/scripts/seedit-installhelper-include.sh


POLICYROOT=/etc/selinux/seedit
SEPOLICYDIR=/usr/share/seedit/sepolicy


initialize_seedit() {

        ### Make binary policy to fit user's environment
        # Make binary policy into /usr/share/seedit/sepolicy
	/usr/sbin/seedit-load -tv -n
	# This is needed to label files that need file type transition configuration
	cat /usr/share/seedit/base_policy/contexts/dynamic_contexts >> $SEPOLICYDIR/file_contexts
	#Copy related file to /etc/selinux
	if [ $MODULAR = "n" ];then \
		cp $SEPOLICYDIR/policy.* $POLICYROOT/policy;\
	fi
	cp $SEPOLICYDIR/file_contexts $POLICYROOT/contexts/files/
	cp $SEPOLICYDIR/customizable_types $POLICYROOT/contexts/files/
	cp $SEPOLICYDIR/userhelper_context $POLICYROOT/contexts
	echo "" >  $POLICYROOT/contexts/files/file_contexts.homedirs
	echo "" >  $POLICYROOT/users/system.users
	echo "" >  $POLICYROOT/users/local.users

	if [ ! -e /usr/share/seedit/sepolicy/file_contexts.m4.old ]; then \
		cp /usr/share/seedit/sepolicy/file_contexts.m4 /usr/share/seedit/sepolicy/file_contexts.m4.old;\
	fi	
	#When using modular policy, we have to install policy.<version> here.
	if [ $MODULAR = "y" ]; then
		/usr/sbin/semodule -b /usr/share/seedit/sepolicy/base.pp -s seedit -n
		cp /usr/share/seedit/sepolicy/file_contexts $POLICYROOT/contexts/files
	fi
	
	###Setup auditd
	#Register dummy audit rule, this is necessary to display PATH entry in log 
	if [ -e $AUDITRULES ]; then
	        cat $AUDITRULES | sed -e 's!-a exit,always -S chroot!!g' > $AUDITRULES.tmp
		mv $AUDITRULES.tmp $AUDITRULES
	 			
		echo "-a exit,always -S chroot" >> $AUDITRULES
	fi
	/sbin/chkconfig auditd on
	

	### Config restorecond
	# label of ld.so.cache can be broken, so have to watch
	if [ -e /etc/selinux/restorecond.conf ];then 
		cat /etc/selinux/restorecond.conf |sed -e 's/^\/etc\/ld.so.cache.*$//'>/etc/selinux/restorecond.conf.tmp
		cp /etc/selinux/restorecond.conf.tmp /etc/selinux/restorecond.conf
	fi
	echo "/etc/ld.so.cache" >> /etc/selinux/restorecond.conf

	#### Config boot option
        ##setup /etc/selinux/conf and automatic relabel
	cat $SELINUXCONF |sed -e 's/^SELINUX=.*$/SELINUX=permissive/'|sed -e 's/^SELINUXTYPE=.*$/SELINUXTYPE=seedit/' >$SELINUXCONF.tmp
	mv $SELINUXCONF $SELINUXCONF.orig
	mv  $SELINUXCONF.tmp $SELINUXCONF
	touch /.autorelabel

	
	#Setup initialization at boot
	echo "/var/tmp/bootstrap.sh" >> /etc/rc.d/rc.local
	# Code related to bootstrap is from Yoichi Hirose <yhirose@users.sourceforge.jp>
	cat << __EOF >/var/tmp/bootstrap.sh

#!/bin/sh
/usr/sbin/seedit-restorecon -R /etc -v
/usr/sbin/seedit-load -v
cat /etc/rc.d/rc.local | sed -e 's!/var/tmp/bootstrap.sh!!g' > /etc/rc.d/rc.local.tmp
rm -f /etc/rc.d/rc.local
mv /etc/rc.d/rc.local.tmp /etc/rc.d/rc.local
/usr/sbin/seedit-restorecon  /etc/rc.d/rc.local -v
chmod 0755 /etc/rc.d/rc.local
rm /usr/share/seedit/sepolicy/need-init
init 6

__EOF

	chmod 755 /var/tmp/bootstrap.sh


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

if [ $1 = "upgrade" ]; then
#Initialization when RBAC enabled
   /usr/sbin/seedit-rbac off -n
   /usr/sbin/seedit-rbac on -n
   rm /usr/share/seedit/sepolicy/need-rbac-init
   /usr/sbin/seedit-load -v	
   exit 0
fi

if [ $1 = "install" ]; then
    initialize_seedit
fi


if [ $1 = "uninstall" ]; then
    uninstall_seedit
fi