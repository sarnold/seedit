#!/bin/sh

#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura
#! 
#! This program is free software; you can redistribute it and/or modify
#! it under the terms of the GNU General Public License as published by
#! the Free Software Foundation; either version 2 of the License, or
#! (at your option) any later version.
#! 
#! This program is distributed in the hope that it will be useful,
#! but WITHOUT ANY WARRANTY; without even the implied warranty of
#! MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#! GNU General Public License for more details.
#! 
#! You should have received a copy of the GNU General Public License
#! along with this program; if not, write to the Free Software
#! Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

POLICY_ROOT=/etc/seedit/policy/


cd $POLICY_ROOT
pwd

if [ $1 = "on" ]; then
    echo "Enabling RBAC"
    echo "Going to permissive mode"
    /usr/sbin/setenforce 0
    mv extras/*_r.sp .
    mv extras/newrole_t.sp .
    mv unconfined_t.sp extras
    mv unconfined_su_t.sp extras
    echo "root:sysadm_r:sysadm_t" >  /etc/selinux/seedit/contexts/userhelper_context
    touch /usr/share/seedit/rbac-on
elif [ $1 = "off" ]; then
    echo "Disabling RBAC"
    echo "Going to permissive mode"
    /usr/sbin/setenforce 0
    mv *_r.sp extras
    mv newrole_t.sp extras
    mv extras/unconfined_t.sp .
    mv extras/unconfined_su_t.sp .
    echo "system_u:system_r:unconfined_t" >  /etc/selinux/seedit/contexts/userhelper_context
    rm -rf /usr/share/seedit/rbac-on
else
    echo "usage:seedit-rbac on|off [-n]"
    exit
fi

skip="n"
if [ $# -gt 2 ]; then  
    if [ $2 = "-n" ]; then
	skip=y
    fi
fi

if [ $skip = "y" ];then
    echo "seedit-load skipped"
else
    /usr/sbin/seedit-load -tv
    /usr/sbin/semodule -b /usr/share/seedit/sepolicy/base.pp -s seedit -n
    touch /.autorelabel
    echo "Done, please reboot"
fi
