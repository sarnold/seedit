#!/bin/sh
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
elif [ $1 = "off" ]; then
    echo "Disabling RBAC"
    echo "Going to permissive mode"
    /usr/sbin/setenforce 0
    mv *_r.sp extras
    mv newrole_t.sp extras
    mv extras/unconfined_t.sp .
    mv extras/unconfined_su_t.sp .
else
    echo "usage:seedit-rbac on|off [-n]"
    exit
fi

if [ $2 = "-n" ]; then
    echo "seedit-load skipped"
else
    /usr/sbin/seedit-load -v
    echo "done, reboot"
fi