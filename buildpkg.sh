#!/bin/sh

. common.sh

mkdir -p archive

name=$1
distro=$DISTRO

if [ -z $name ]; then 
    echo "Usage buildpkg <packagename> "
fi

if [ -e $name-$VERSION ]
then 
rm -rf $name-$VERSION
fi

cp -r $name $name-$VERSION

if [ -e $name-$VERSION-$RELEASE.tar.gz ]
then
	rm $name-$VERSION-$RELEASE.tar.gz
fi
tar czvf $name-$VERSION-$RELEASE.tar.gz $name-$VERSION
mv $name-$VERSION-$RELEASE.tar.gz archive
rm -rf $name-$VERSION

cd archive
rpmbuild -ta $name-$VERSION-$RELEASE.tar.gz

if [ -e ~/rpm/RPMS/i386/$name-$VERSION-$RELEASE.i386.rpm ]; then
    mv ~/rpm/RPMS/i386/$name-$VERSION-$RELEASE.i386.rpm .
fi
if [ -e ~/rpm/RPMS/noarch/$name-$VERSION-$RELEASE.noarch.rpm ]; then
    mv ~/rpm/RPMS/noarch/$name-$VERSION-$RELEASE.noarch.rpm .
fi
if [ -e ~/rpm/SRPMS/$name-$VERSION-$RELEASE.src.rpm ]; then
    mv ~/rpm/SRPMS/$name-$VERSION-$RELEASE.src.rpm .
fi

if [ -e ~/rpm/RPMS/i386/$name-$VERSION-$RELEASE.$distro.i386.rpm ]; then
    mv ~/rpm/RPMS/i386/$name-$VERSION-$RELEASE.$distro.i386.rpm .
fi
if [ -e ~/rpm/RPMS/noarch/$name-$VERSION-$RELEASE.$distro.noarch.rpm ]; then
    mv ~/rpm/RPMS/noarch/$name-$VERSION-$RELEASE.$distro.noarch.rpm .
fi
if [ -e ~/rpm/SRPMS/$name-$VERSION-$RELEASE.$distro.src.rpm ]; then
    mv ~/rpm/SRPMS/$name-$VERSION-$RELEASE.$distro.src.rpm .
fi


mv  $name-$VERSION-$RELEASE.tar.gz source
