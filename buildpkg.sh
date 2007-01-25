#!/bin/sh

#Fix these valuables for your environment
VERSION=2.1.0
BETA=-beta6.5
DISTRO=fc6
SAMPLE_POLICY_TYPE=fc6
RELEASE=1
PYTHON_VER=2.4
AUDITCONF=\\/etc\\/audit\\/audit.rules
MODULAR=y
CUSTOMIZABLE_TYPES=y
PAM_INCLUDE_SUPPORT=y
SVNROOT=~/seedit/trunk/
RPMROOT=~/rpm


mkdir -p archive

distro=$DISTRO

rm -rf build
svn export $SVNROOT build

cd build
cat seedit.spec|sed -e "s/^%define distro.*\$/%define distro $DISTRO/"|sed -e "s/^%define auditrules.*\$/%define auditrules $AUDITCONF/"|sed -e "s/^%define modular.*\$/%define modular $MODULAR/"|sed -e "s/^%define python_ver.*\$/%define python_ver $PYTHON_VER/"|sed -e "s/^%define customizable_types.*\$/%define customizable_types $CUSTOMIZABLE_TYPES/"|sed -e "s/^%define pam_include_support.*\$/%define pam_include_support $PAM_INCLUDE_SUPPORT/"|sed -e "s/^%define sample_policy_type.*\$/%define sample_policy_type $SAMPLE_POLICY_TYPE/">seedit.spec.tmp

mv seedit.spec.tmp seedit.spec
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

rpmbuild -ba $RPMROOT/SPECS/seedit.spec
cd archive
cp  $RPMROOT/RPMS/i386/seedit*$VERSION*.i386.rpm .
cp  $RPMROOT/SRPMS/seedit-$VERSION*.src.rpm .
cp $RPMROOT/SPECS/seedit.spec .
rm *debuginfo*.rpm seedit-gui.desktop seedit-gui.png
