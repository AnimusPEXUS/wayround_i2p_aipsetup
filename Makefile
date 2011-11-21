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
# end of settings

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

help: default

install: clean
	@echo "<<<[ Installing ]>>>"
	-rm -rf "$(PREFIX)/$(AIP_B)"
	mkdir -p "$(PREFIX)/$(AIP_B)"
	cp -r * "$(PREFIX)/$(AIP_B)"
	chmod -R 755 "$(PREFIX)/$(AIP_B)"
	@echo "<<<[ Installed ]>>>"
	$(MAKE) -C "$(PREFIX)/$(AIP_B)" setup

setup:
	@echo "<<<[ Setting Up ]>>>"
	@echo "setting base folder to $(AIP_B)"
	-mkdir -p "$(PREFIX)/$(AIP_B)"
	-mkdir -p "$(PREFIX)/$(BINDIR)"
	cat aipsetup | sed -e "4{s#export AIP_DIR=\"\"#export AIP_DIR=\"$(AIP_B)\"#}" > "$(PREFIX)/$(BINDIR)/aipsetup"
	chown 0:0 "$(PREFIX)/$(BINDIR)/aipsetup"
	chmod -R 0755 "$(PREFIX)/$(BINDIR)/aipsetup"
	@echo "<<<[ Sett Up ]>>>"

unsetup:
	-rm "$(PREFIX)/$(BINDIR)/aipsetup"

clean:
	chown -R "`id -u`:`id -g`" .
	find -type -d '!' -name '.' '!' -name '..' -exec chmod 700 '{}' ';'
	find -type -f -exec chmod 600 '{}' ';'
	find -type f '(' -name '*~' -o -name '*#' ')' -exec rm -v '{}' ';'

# release: clean
# 	echo "$(VERSION)" > ./VERSION
# 	cd .. && cp -a ./aipsetup "./aipsetup-$(VERSION)"
# 	cd .. && tar -c "./aipsetup-$(VERSION)" | xz -9v > "aipsetup-$(VERSION).tar.xz"
# 	cd .. && rm -r "./aipsetup-$(VERSION)"
