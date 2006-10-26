#!/bin/sh
MODULES="seedit-converter seedit-policy seedit-gui seedit-doc"
. common.sh

mkdir -p archive
echo $DISTRO
exit
#rewrite %{distro} %{auditrules}
for name in $MODULES
do
  cd $name
  cat $name.spec|sed -e "s/^%define distro.*\$/%define distro $DISTRO/"|sed -e "s/^%define auditrules.*\$/%define auditrules $AUDITCONF/">$name.spec.tmp
  mv $name.spec.tmp $name.spec
  cd ..
done



# make tar ball
for name in $MODULES
do
echo $name
if [ -e $name-$VERSION ]
then 
rm -rf $name-$VERSION
fi

cp -r $name $name-$VERSION

if [ -e $name-$VERSION.tar.gz ]
then
	rm $name-$VERSION.tar.gz
fi

tar czvf $name-$VERSION-$RELEASE.tar.gz $name-$VERSION
mv $name-$VERSION-$RELEASE.tar.gz archive
rm -rf $name-$VERSION
done

