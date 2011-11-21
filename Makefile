# settings
ifndef PREFIX
PREFIX = /
endif

ifndef AIP_B
AIP_B = /usr/lib/aipsetup
endif

ifndef BINDIR
BINDIR = /usr/bin
endif
# end settings

PPWD = `pwd`

VERSION = `date +%Y.%m.%d.%H.%M`

default:
	@printf "aipsetup " ; cat VERSION ; echo
	@printf "when installing:\n"
	@printf "\tmake install     - install to PREFIX/AIP_B dir and 'make setup' it\n"
	@printf "\n"
	@printf "when installed:\n"
	@printf "\tmake setup       - setup to BINDIR\n"
	@printf "\tmake unsetup     - unset from BINDIR\n"
	@printf "\n"
	@printf "while changing:\n"
	@printf "\tmake clean       - clean current dir of junk\n"
	@printf "\tmake release     - clean and pack into release\n"
	@printf "\n"
	@printf "by default:\n"
	@printf "\tPREFIX == $(PREFIX)\n"
	@printf "\tAIP_B == $(AIP_B)\n"
	@printf "\tBINDIR == $(BINDIR)\n"

install: clean
	@echo "<<<[ Installing ]>>>"
	-rm -rf "$(PREFIX)/$(AIP_B)"
	mkdir -p "$(PREFIX)/$(AIP_B)"
	cp -r * "$(PREFIX)/$(AIP_B)"
	@echo "<<<[ Installed ]>>>"
	$(MAKE) -C "$(PREFIX)/$(AIP_B)" setup

setup:
	@echo "<<<[ Setting Up ]>>>"
	@echo "setting base folder to $(AIP_B)"
	-mkdir -p "$(PREFIX)/$(AIP_B)"
	-mkdir -p "$(PREFIX)/$(BINDIR)"
	cat aipsetup | sed -e "4{s#export AIP_DIR=\"\"#export AIP_DIR=\"$(AIP_B)\"#}" > "$(PREFIX)/$(BINDIR)/aipsetup"
	chown 0:0 "$(PREFIX)/$(BINDIR)/aipsetup"
	chmod 0700 "$(PREFIX)/$(BINDIR)/aipsetup"
	@echo "<<<[ Sett Up ]>>>"

unsetup:
	-rm "$(PREFIX)/$(BINDIR)/aipsetup"

clean:
	chown -R 0:0 .
	chmod -R 0600 .
	find -type f -name '*~' -exec rm -v '{}' ';'

release: clean
	echo "$(VERSION)" > ./VERSION
	cd .. && cp -a ./aipsetup "./aipsetup-$(VERSION)"
	cd .. && tar -c "./aipsetup-$(VERSION)" | xz -9v > "aipsetup-$(VERSION).tar.xz"
	cd .. && rm -r "./aipsetup-$(VERSION)"
