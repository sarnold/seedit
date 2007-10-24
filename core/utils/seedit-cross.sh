#!/bin/sh
# This program is helper for cross-development of policy
# usage
# seedit-cross.sh build
#   generates policy under sepolicy dir
# seedit-cross.sh install
#   installs generated policy to $POLICYROOT

M4=m4

CONVERTER=./seedit-converter
CHECKPOLICY=/usr/bin/checkpolicy
POLICYROOT=./policy_root
POLICYDIR=$POLICYROOT/policy
CONTEXTSDIR=$POLICYROOT/contexts
CONFDIR=./simplified_policy
BASEPOLICYDIR=./base_policy
MACRODIR=./macros
OUTDIR=./sepolicy
INSTALL_PATH=$POLICYROOT
POLICYVER=21
OLD_FILE_CONTEXTS=$OUTDIR/file_contexts.m4.old
FILE_CONTEXTS=$OUTDIR/file_contexts.m4


do_diff() {
    diffstr=""
    diff $OLD_FILE_CONTEXTS $FILE_CONTEXTS -r |cat >  fcdiff.m4.tmp
    m4  -Imacros -s $MACRODIR/mcs_macros.te fcdiff.m4.tmp > fcdiff.pre.tmp
    cat fcdiff.pre.tmp |grep -e "^[<>]"|sed -e 's/^[><][ \t]*//'|sed -e 's/[ \t]\+.*//'|sed -e 's/(.*//'|sort|sed s/"\[\^\/\]"//g > fcdiff.tmp   
    mv fcdiff.tmp $OUTDIR/fcdiff
    cp $FILE_CONTEXTS $OLD_FILE_CONTEXTS

}

do_convert() {
	mkdir -p $OUTDIR;

	m4 -s $CONFDIR/*.sp >$CONFDIR/all.sp;        
        #$CONVERTER -p -i $CONFDIR/all.sp -o ./sepolicy -b ./base_policy -I  $CONFDIR/include
	#$CONVERTER --disable-boolean -t 1 -i $CONFDIR/all.sp -o $OUTDIR -b $BASEPOLICYDIR -I $CONFDIR/include  --profile-data $OUTDIR/profile.data
	if $CONVERTER --disable-boolean -i $CONFDIR/all.sp -o $OUTDIR -b $BASEPOLICYDIR -I $CONFDIR/include -c dynamic_contexts; then
		echo ""	
	else
		exit 1
	fi 
	$M4  -Imacros -s $MACRODIR/*.te $OUTDIR/generated.conf > $OUTDIR/policy.conf;
	$M4  -Imacros -s $MACRODIR/mcs_macros.te $OUTDIR/file_contexts.m4 > $OUTDIR/file_contexts;
	$M4  -Imacros -s $MACRODIR/mcs_macros.te $OUTDIR/userhelper_context.m4 > $OUTDIR/userhelper_context.tmp;
	grep system_u $OUTDIR/userhelper_context.tmp >  $OUTDIR/userhelper_context

	rm $OUTDIR/userhelper_context.tmp
	$CHECKPOLICY -o $OUTDIR/policy.$POLICYVER -c $POLICYVER $OUTDIR/policy.conf
	mkdir -p $OUTDIR/policy
	mkdir -p $OUTDIR/contexts/files
	cp $OUTDIR/policy.$POLICYVER $OUTDIR/policy
	cp $OUTDIR/file_contexts $OUTDIR/contexts/files
	cp $OUTDIR/customizable_types $OUTDIR/contexts
	if [ ! -e $OLD_FILE_CONTEXTS ]; then
	    cp $FILE_CONTEXTS $OLD_FILE_CONTEXTS
        fi
}

do_install() {
	mkdir -p $POLICYROOT/users
	mkdir -p $POLICYDIR
	mkdir -p $CONTEXTSDIR/files
	cp $OUTDIR/fcdiff $POLICYROOT
	cp $OUTDIR/policy.$POLICYVER $POLICYDIR
	cp $OUTDIR/file_contexts $CONTEXTSDIR/files/
	cp $OUTDIR/customizable_types $CONTEXTSDIR
	cp $OUTDIR/userhelper_context $CONTEXTSDIR
	cp -r $BASEPOLICYDIR/contexts/*  $CONTEXTSDIR
	echo "" > $CONTEXTSDIR/files/file_contexts.homedirs
	echo "#" >  $POLICYROOT/users/system.users
	echo "#" >  $POLICYROOT/users/local.users
}


if [ $1 == "build" ] 
then
    do_convert
fi

if [ $1 == "diff" ] 
then
    do_diff
fi

if [ $1 == "install" ] 
then
    do_install
fi
