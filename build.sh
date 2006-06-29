MODULES="seedit-converter seedit-policy"
VERSION=2.0.0.rc1
DISTRO=FC5

mkdir -p archive/source
mkdir -p archive/RPM

cd archive
rpmbuild -ta seedit-converter-$VERSION.tar.gz 
rpmbuild -ta seedit-policy-$VERSION.tar.gz 
rpmbuild -ta seedit-gui-$VERSION.tar.gz 
rpmbuild -ta seedit-doc-$VERSION.tar.gz 

mv ~/rpm/RPMS/i386/seedit-converter-$VERSION-$DISTRO.i386.rpm ./RPM
mv ~/rpm/RPMS/noarch/seedit-policy-$VERSION-$DISTRO.noarch.rpm ./RPM
mv ~/rpm/RPMS/noarch/seedit-gui-$VERSION-1.noarch.rpm ./RPM
mv ~/rpm/RPMS/noarch/seedit-doc-$VERSION-1.noarch.rpm ./RPM
mv ~/rpm/SRPMS/seedit-converter-$VERSION-$DISTRO.src.rpm ./source
mv ~/rpm/SRPMS/seedit-policy-$VERSION-$DISTRO.src.rpm ./source
mv ~/rpm/SRPMS/seedit-gui-$VERSION-1.src.rpm ./source
mv ~/rpm/SRPMS/seedit-doc-$VERSION-1.src.rpm ./source




