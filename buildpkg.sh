#!/bin/sh

#Fix these valuables for your environment
VERSION=2.1.0
BETA=-beta6
DISTRO=fc6
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
cat seedit.spec|sed -e "s/^%define distro.*\$/%define distro $DISTRO/"|sed -e "s/^%define auditrules.*\$/%define auditrules $AUDITCONF/"|sed -e "s/^%define modular.*\$/%define modular $MODULAR/"|sed -e "s/^%define python_ver.*\$/%define python_ver $PYTHON_VER/"|sed -e "s/^%define customizable_types.*\$/%define customizable_types $CUSTOMIZABLE_TYPES/"|sed -e "s/^%define pam_include_support.*\$/%define pam_include_support $PAM_INCLUDE_SUPPORT/">seedit.spec.tmp
mv seedit.spec.tmp seedit.spec
cp seedit.spec $RPMROOT/SPECS
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
tar czvf seedit-$VERSION$BETA.tar.gz seedit-$VERSION
cp seedit-$VERSION$BETA.tar.gz archive
mv seedit-$VERSION$BETA.tar.gz $RPMROOT/SOURCES
rm -rf seedit-$VERSION
cp gui/desktop/seedit-gui.desktop $RPMROOT/SOURCES
cp gui/icons/seedit-gui.png $RPMROOT/SOURCES


rpmbuild -ba $RPMROOT/SPECS/seedit.spec
rpmbuild -ba $RPMROOT/SPECS/seedit.spec --target noarch
cd archive
cp  $RPMROOT/RPMS/i386/seedit-$VERSION*$DISTRO.i386.rpm .
cp  $RPMROOT/RPMS/noarch/seedit-*$VERSION*$DISTRO.noarch.rpm .
cp  $RPMROOT/SRPMS/seedit-$VERSION*$DISTRO.src.rpm .
rm *debuginfo*.rpm seedit-gui.desktop seedit-gui.png
