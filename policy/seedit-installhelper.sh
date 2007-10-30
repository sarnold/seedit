#!/bin/sh
# Helper to install/uninstall seedit
#define below
#SELINUXCONF=/etc/selinux/config
#AUDITRULES=/etc/audit/audit.rules
#MODULAR=n
. /usr/share/seedit/initialize/seedit-installhelper-include.sh


POLICYROOT=/etc/selinux/seedit
SEPOLICYDIR=/usr/share/seedit/sepolicy
SETFILES=/usr/sbin/setfiles
SELINUXENABLED=/usr/sbin/selinuxenabled

initialize_seedit() {
 
 #If RBAC related file is remaining, remove it. RBAC is disabled by default.
 if [ -e /etc/seedit/policy/sysadm_r.sp ]; then
  /usr/sbin/seedit-rbac off -n    
  rm -rf /usr/share/seedit/rbac-on
 fi
 if [ -e /usr/share/seedit/rbac-on ]; then
  /usr/sbin/seedit-rbac off -n    
 fi
        ### Make binary policy to fit user's environment
        # Make binary policy into /usr/share/seedit/sepolicy
 /usr/sbin/seedit-load -d -v
 
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

 ### Initialize for Asianux 2
 if [ $DISTRO = "ax2" ]; then
      if   $SELINUXENABLED ; then
   echo "Do nothing"
      else
   echo "Initializing SELinux label, it will take some minutes"
   FILESYSTEMS=`mount | grep -v "context=" | egrep -v '\((|.*,)bind(,.*|)\)' | awk '/(ext[23]| xfs | jfs ).*\(rw/{print $3}';`
   $SETFILES -v /etc/selinux/seedit/contexts/files/file_contexts $FILESYSTEMS
      fi
 fi
 rm /usr/share/seedit/sepolicy/need-init
 /sbin/chkconfig setroubleshoot off
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
   if [ -e /usr/share/seedit/rbac-on ]; then
 /usr/sbin/seedit-rbac off -n
 /usr/sbin/seedit-rbac on -n
   else
        /usr/sbin/seedit-rbac off -n
   fi
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
