MODULES="seedit-converter seedit-policy"
VERSION=2.0.0.b7

mkdir -p archive

cd archive
rpmbuild -ta seedit-converter-$VERSION.tar.gz 
rpmbuild -ta seedit-policy-$VERSION.tar.gz 
rpmbuild -ta seedit-gui-$VERSION.tar.gz 

mv ~/rpm/RPMS/i386/seedit-converter-$VERSION-FC5.i386.rpm .
mv ~/rpm/RPMS/noarch/seedit-policy-$VERSION-FC5.noarch.rpm .
mv ~/rpm/RPMS/noarch/seedit-gui-$VERSION-1.noarch.rpm .
mv ~/rpm/SRPMS/seedit-converter-$VERSION-FC5.src.rpm .
mv ~/rpm/SRPMS/seedit-policy-$VERSION-FC5.src.rpm .
mv ~/rpm/SRPMS/seedit-gui-$VERSION-1.src.rpm .



