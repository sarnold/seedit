#!/bin/sh

#Fix these valuables for your environment
VERSION=2.1.0
BETA=-beta7
DISTRO=ax2
SAMPLE_POLICY_TYPE=ax2
#AUDITCONF=\\%\\{_sysconfdir\\}\\/audit\\/audit.rules
AUDITCONF=\\%\\{_sysconfdir\\}\\/audit.rules
MODULAR=n
CUSTOMIZABLE_TYPES=n
PAM_INCLUDE_SUPPORT=n
AUDIT_OBJ_TYPE_SUPPORT=n
SVNROOT=~/seedit/trunk/
RPMROOT=~/rpm


mkdir -p archive

distro=$DISTRO

rm -rf build
svn export $SVNROOT build

cd build

#Asianux2 specific
if [ $DISTRO = "ax2" ]
then 
cat seedit.spec|sed -e "s/^Requires:.*desktop-file-utils.*\$//">seedit.spec.tmp
mv seedit.spec.tmp seedit.spec
cat seedit.spec|sed -e "s/^desktop-file-install.*\$//">seedit.spec.tmp
mv seedit.spec.tmp seedit.spec
cat seedit.spec|sed -e "s/^#AX2\$//">seedit.spec.tmp
mv seedit.spec.tmp seedit.spec
fi
cat seedit.spec|sed -e "s/^%define auditrules.*\$/%define auditrules $AUDITCONF/"|sed -e "s/^%define modular.*\$/%define modular $MODULAR/"|sed -e "s/^%define customizable_types.*\$/%define customizable_types $CUSTOMIZABLE_TYPES/"|sed -e "s/^%define pam_include_support.*\$/%define pam_include_support $PAM_INCLUDE_SUPPORT/"|sed -e "s/^%define sample_policy_type.*\$/%define sample_policy_type $SAMPLE_POLICY_TYPE/"|sed -e "s/^%define audit_obj_type_support.*\$/%define audit_obj_type_support $AUDIT_OBJ_TYPE_SUPPORT/">seedit.spec.tmp
mv seedit.spec.tmp seedit.spec

if [ $PAM_INCLUDE_SUPPORT = "n" ]
then
cat seedit.spec|sed -e "s/^Requires:.*pam.*\$//">seedit.spec.tmp
mv seedit.spec.tmp seedit.spec
fi


mv seedit.spec $RPMROOT/SPECS
chmod 644 $RPMROOT/SPECS/seedit.spec
cd ..

if [ -e seedit-$VERSION ]
then 
rm -rf seedit-$VERSION
fi

rm -rf build/docs
cp -r build seedit-$VERSION

if [ -e seedit-$VERSION.tar.gz ]
then
 rm seedit-$VERSION.tar.gz
fi
mv seedit-$VERSION/gui/desktop/seedit-gui.desktop $RPMROOT/SOURCES
mv seedit-$VERSION/gui/icons/seedit-gui.png $RPMROOT/SOURCES
tar czvf seedit-$VERSION$BETA.tar.gz seedit-$VERSION
cp seedit-$VERSION$BETA.tar.gz archive
mv seedit-$VERSION$BETA.tar.gz $RPMROOT/SOURCES
rm -rf seedit-$VERSION

rpmbuild -ba $RPMROOT/SPECS/seedit.spec --define "dist.$DISTRO"
cd archive
cp  $RPMROOT/RPMS/i386/seedit*$VERSION*.i386.rpm .
cp  $RPMROOT/SRPMS/seedit-$VERSION*.src.rpm .
cp $RPMROOT/SPECS/seedit.spec .
rm *debuginfo*.rpm seedit-gui.desktop seedit-gui.png
