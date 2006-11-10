#!/bin/sh

. common.sh

mkdir -p archive

name=$1
distro=$DISTRO

if [ -z $name ]; then 
    echo "Usage buildpkg <packagename> "
fi

rm -rf $name
svn export $SVNROOT/$name $name
mkdir -p archive
rm archive/$name*

cd $name
cat $name.spec|sed -e "s/^%define distro.*\$/%define distro $DISTRO/"|sed -e "s/^%define auditrules.*\$/%define auditrules $AUDITCONF/"|sed -e "s/^%define modular.*\$/%define modular $MODULAR/"|sed -e "s/^%define python_ver.*\$/%define python_ver $PYTHON_VER/"|sed -e "s/^%define customizable_types.*\$/%define customizable_types $CUSTOMIZABLE_TYPES/">$name.spec.tmp
mv $name.spec.tmp $name.spec
cd ..



if [ -e $name-$VERSION ]
then 
rm -rf $name-$VERSION
fi

cp -r $name $name-$VERSION

if [ -e $name-$VERSION.tar.gz ]
then
	rm $name-$VERSION.tar.gz
fi
tar czvf $name-$VERSION$BETA.tar.gz $name-$VERSION
mv $name-$VERSION$BETA.tar.gz archive
rm -rf $name-$VERSION

if [ $name = "seedit-gui" ]
then
	cp seedit-gui/desktop/seedit-gui.desktop archive
	cp seedit-gui/icons/seedit-gui.png archive
fi

cd archive
rpmbuild -ta $name-$VERSION$BETA.tar.gz

cp  ~/rpm/RPMS/i386/$name-$VERSION-*$DISTRO.i386.rpm .
cp  ~/rpm/RPMS/noarch/$name-$VERSION-*$DISTRO.noarch.rpm .
cp  ~/rpm/SRPMS/$name-$VERSION-*$DISTRO.src.rpm .
