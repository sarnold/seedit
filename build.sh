VERSION=2.0.0.rc2
RELEASE=1
DISTRO=FC5

mkdir -p archive/source
mkdir -p archive/RPM

cd archive
rpmbuild -ta seedit-converter-$VERSION.tar.gz 
rpmbuild -ta seedit-policy-$VERSION.tar.gz 
rpmbuild -ta seedit-gui-$VERSION.tar.gz 
rpmbuild -ta seedit-doc-$VERSION.tar.gz 

mv ~/rpm/RPMS/i386/seedit-converter-$VERSION-$RELEASE.$DISTRO.i386.rpm ./RPM
mv ~/rpm/RPMS/noarch/seedit-policy-$VERSION-$RELEASE.$DISTRO.noarch.rpm ./RPM
mv ~/rpm/RPMS/noarch/seedit-gui-$VERSION-$RELEASE.noarch.rpm ./RPM
mv ~/rpm/RPMS/noarch/seedit-doc-$VERSION-$RELEASE.noarch.rpm ./RPM
mv ~/rpm/SRPMS/seedit-converter-$VERSION-$RELEASE.$DISTRO.src.rpm ./source
mv ~/rpm/SRPMS/seedit-policy-$VERSION-$RELEASE.$DISTRO.src.rpm ./source
mv ~/rpm/SRPMS/seedit-gui-$VERSION-$RELEASE.src.rpm ./source
mv ~/rpm/SRPMS/seedit-doc-$VERSION-$RELEASE.src.rpm ./source




