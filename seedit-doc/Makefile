prefix=/usr
INSTALLPATH= $(prefix)/share/doc/seedit

all:
	$(MAKE) -C tutorial
	$(MAKE) -C tutorial/ja
	$(MAKE) -C spdl_spec
	$(MAKE) -C rbac


install:all
	mkdir -p $(INSTALLPATH) 
	$(MAKE) -C tutorial install
	$(MAKE) -C tutorial/ja install
	$(MAKE) -C spdl_spec install
	$(MAKE) -C rbac install
	install -m 644 README $(INSTALLPATH)
	install -m 644 README.ja $(INSTALLPATH)

clean:
	$(MAKE) -C tutorial clean
	$(MAKE) -C tutorial/ja clean
	$(MAKE) -C spdl_spec clean
	$(MAKE) -C rbac clean