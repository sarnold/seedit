VERSION=2.0.0
RELEASE=2

mkdir -p archive

name=$1
if [ ! -n name ]; then 
    echo "Usage buildpkg <packagename> <distro>"
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
    mv ~/rpm/RPMS/i386/$name-$VERSION-$RELEASE.i386.rpm ./RPM
fi
if [ -e ~/rpm/RPMS/noarch/$name-$VERSION-$RELEASE.i386.rpm ]; then
    mv ~/rpm/RPMS/noarch/$name-$VERSION-$RELEASE.i386.rpm ./RPM
fi
if [ -e ~/rpm/SRPMS/noarch/$name-$VERSION-$RELEASE.src.rpm ]; then
    mv ~/rpm/SRPMS/noarch/$name-$VERSION-$RELEASE.src.rpm ./source
fi
