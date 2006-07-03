prefix=/usr
INSTALLPATH= $(prefix)/share/doc/seedit

all:
	$(MAKE) -C tutorial
	$(MAKE) -C tutorial/ja
	$(MAKE) -C spdl_spec
	$(MAKE) -C rbac
upload: 
	mkdir -p upload
	mv tutorial/tutorial.pdf upload
	mv tutorial/tutorial upload
	mv tutorial/ja/tutorial_jp.pdf upload
	mv tutorial/ja/tutorial_jp upload
	mv spdl_spec/*.pdf upload
	mv spdl_spec/spdl_spec upload
	mv rbac/rbac_guide.pdf	upload
	mv rbac/rbac_guide	upload

doc:
	$(MAKE) -C tutorial html pdf
	$(MAKE) -C tutorial/ja html pdf
	$(MAKE) -C spdl_spec html pdf
	$(MAKE) -C rbac html pdf

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
