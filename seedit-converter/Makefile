

all:
	$(MAKE) -C lib
	$(MAKE) -C converter
	$(MAKE) -C xml
	$(MAKE) -C utils
	$(MAKE) -C restorecon
	$(MAKE) -C config

install: all
	$(MAKE) -C lib install
	$(MAKE) -C converter install
	$(MAKE) -C xml install
	$(MAKE) -C utils install 
	$(MAKE) -C restorecon install
	$(MAKE) -C config install

uninstall:
	$(MAKE) -C lib uninstall
	$(MAKE) -C converter uninstall
	$(MAKE) -C xml uninstall
	$(MAKE) -C utils uninstall 

clean:
	$(MAKE) -C lib clean
	$(MAKE) -C converter clean
	$(MAKE) -C xml clean
	$(MAKE) -C utils clean
	$(MAKE) -C restorecon clean

