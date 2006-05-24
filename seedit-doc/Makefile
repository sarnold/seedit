datadir=/usr/share

build:
	rm -rf build
	mkdir build
	cp -r install build
	cp -r manual build
	cp -r tutorial build
	cd simplified_policy/manual;\
	make install INSTALLDIR=../../build;\
	cd euc_jp;\
	make install INSTALLDIR=../../../build

install: build
	mkdir -p $(datadir)/doc/seedit-doc
	cp -r build/* $(datadir)/doc/seedit-doc


