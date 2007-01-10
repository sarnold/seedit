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

mkdir -p archive

distro=$DISTRO

rm -rf seedit
svn export $SVNROOT seedit

cd seedit
cat seedit.spec|sed -e "s/^%define distro.*\$/%define distro $DISTRO/"|sed -e "s/^%define auditrules.*\$/%define auditrules $AUDITCONF/"|sed -e "s/^%define modular.*\$/%define modular $MODULAR/"|sed -e "s/^%define python_ver.*\$/%define python_ver $PYTHON_VER/"|sed -e "s/^%define customizable_types.*\$/%define customizable_types $CUSTOMIZABLE_TYPES/"|sed -e "s/^%define pam_include_support.*\$/%define pam_include_support $PAM_INCLUDE_SUPPORT/">seedit.spec.tmp
mv seedit.spec.tmp seedit.spec
cd ..

if [ -e seedit-$VERSION ]
then 
rm -rf seedit-$VERSION
fi

cp -r seedit seedit-$VERSION

if [ -e seedit-$VERSION.tar.gz ]
then
	rm seedit-$VERSION.tar.gz
fi
tar czvf seedit-$VERSION$BETA.tar.gz seedit-$VERSION
mv seedit-$VERSION$BETA.tar.gz archive
rm -rf seedit-$VERSION
cp gui/desktop/seedit-gui.desktop archive
cp gui/icons/seedit-gui.png archive

cd archive
rpmbuild -ta seedit-$VERSION$BETA.tar.gz
rpmbuild -ta seedit-$VERSION$BETA.tar.gz --target noarch
cp  ~/rpm/RPMS/i386/seedit-$VERSION*$DISTRO.i386.rpm .
cp  ~/rpm/RPMS/noarch/seedit-*$VERSION*$DISTRO.noarch.rpm .
cp  ~/rpm/SRPMS/seedit-$VERSION*$DISTRO.src.rpm .
rm *debuginfo*.rpm seedit-gui.desktop seedit-gui.png
