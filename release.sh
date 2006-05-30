MODULES="seedit-converter seedit-policy"
VERSION=2.0.0.b4

mkdir -p archive

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

tar czvf $name-$VERSION.tar.gz $name-$VERSION
mv $name-$VERSION.tar.gz archive
rm -rf $name-$VERSION
done

