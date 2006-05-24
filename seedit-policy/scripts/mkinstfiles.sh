#!/bin/sh
# (c) Yuichi Nakamura himainu-ynakam@miomio.jp
DISTRO=
DEVEL=
TYPE=
SELINUXTYPE=

#following are moved to unused 
FC3_UNUSED="auditd_t.a proftpd_t.a udev_t.a"
FC4_UNUSED="proftpd_t.a dhcpcd_t.a"
AX2_UNUSED="dhcpcd_t.a auditd_t.a"
TL10S_UNUSED="auditd_t.a iiimd_t.a udev_t.a dovecot_t.a dhclient_t.a"
EASY_UNUSED="mail_t.a newrole_t.a run_init_t.a staff_r.a su_t.a sysadm_r.a user_r.a "
STRICT_UNUSED="unconfined_t.a dummy_role_r.a"
UNUSED=""

##following are defined for m4
FC4_DEFINE="fc4 usekudzu"
AX2_DEFINE="ax2 usekdm usekudzu apache_priv apache_snmp"
TL10S_DEFINE="tl10s oldrestorecon usexfree"
EASY_DEFINE="norbac"
STRICT_DEFINE=""
DEFINE=""

install_simplified_policy(){
    FILES=`/bin/ls src/simplified_policy`
    for FILE in $FILES
      do
      if [ -d $FILE ]
	  then
	  continue
      fi
      EXIST=0
      for NAME in $UNUSED
	do
	if [ $NAME = $FILE ]
	    then 
	    EXIST=1	
	else
	    :
	fi 	
      done
      if [ $EXIST = 0 ]
	  then 
	  if [ $DEVEL = 1 ]
	      then
	      cp -r "src/simplified_policy/$FILE"  "policy/simplified_policy"
	  else
	      m4   ./src/macros/template_macros.te $DEFINE "src/simplified_policy/$FILE" > "policy/simplified_policy/$FILE"
	  fi
      else
	  if [ $DEVEL = 1 ]
	      then
	      cp -r  "src/simplified_policy/$FILE" "policy/simplified_policy/unused/$FILE"		
	  else		
	      m4  ./src/macros/template_macros.te $DEFINE "src/simplified_policy/$FILE"> "policy/simplified_policy/unused/$FILE"
	  fi
      fi
    done

    if [ $DEVEL = 1 ]
	then
	cp -r src/simplified_policy/CVS policy/simplified_policy/CVS
    fi
}


if [ -z $3 ]; then
    echo "usage <distro> <develflag: 1or0> <type: strict or easy>"
    exit 1
fi

DISTRO=$1
DEVEL=$2
TYPE=$3
SELINUXTYPE=$4
DISTRO=`echo $DISTRO | tr "a-z" "A-Z"`
TYPE=`echo $TYPE | tr "a-z" "A-Z"`
echo "DISTRO=$DISTRO : DEVEL=$DEVEL: TYPE=$TYPE"


eval "UNUSED=$"$DISTRO"_UNUSED"
eval "tmp=$"$TYPE"_UNUSED"
UNUSED="$UNUSED $tmp"

eval "TMP=$"$DISTRO"_DEFINE"
for d in $TMP
do
	DEFINE="$DEFINE -D $d"
done
eval "TMP=$"$TYPE"_DEFINE"
for d in $TMP
do
 	DEFINE="$DEFINE -D $d"
done

echo $UNUSED
echo $DEFINE

rm -rf policy/*
mkdir -p policy/simplified_policy/unused
install_simplified_policy
cp -r src/base_policy policy
cp -r src/macros policy

./scripts/genmacro.py -i src/base_policy/spdl_spec.xml -m expand > policy/base_policy/spdl_spec.xml
#./scripts/genmacros.pl -i policy/base_policy >> policy/macros/seedit_macros.te
if [ $DISTRO = "TL10S" ] 
    then
    cat Makefile.user |sed -e "s/^RESTORECON=.*\$/RESTORECON=\.\/restorecon/"> Makefile.user.new
    mv Makefile.user.new Makefile.user
fi


cat Makefile.user |sed -e "s/^M4DEFINE=.*\$/M4DEFINE=$DEFINE/"|sed -e "s/^SELINUXTYPE=.*\$/SELINUXTYPE=$SELINUXTYPE/">policy/Makefile
