# settings
ifndef PREFIX
PREFIX = "/"
endif

ifndef AIP_B
AIP_B = "/usr/lib/aipsetup"
endif

ifndef BINDIR
BINDIR = "/usr/bin"
endif
# end settings

PPWD = "`pwd`"

VERSION = "`date +%Y.%m.%d.%H.%M`"

default:
	@printf "aipsetup " ; cat VERSION ; echo
	@printf "when installing:\n"
	@printf "\tmake install     - install to PREFIX/AIP_B dir and 'make setup' it\n"
# 	@printf "\tmake uninstall   - 'make unsetup' and remove PREFIX/AIP_B dir\n"
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

install:
	@echo "<<<[ Installing ]>>>"
	-rm -rf "$(PREFIX)/$(AIP_B)"
	mkdir -p "$(PREFIX)/$(AIP_B)"
	cp -r * "$(PREFIX)/$(AIP_B)"
	@echo "<<<[ Installed ]>>>"
	$(MAKE) -C "$(PREFIX)/$(AIP_B)" setup

# uninstall: unset
# 	-rm -rf *

setup:
	@echo "<<<[ Setting Up ]>>>"
	@echo "setting base folder to $(PPWD)"
	-mkdir -p "$(PREFIX)/$(AIP_B)"
	-mkdir -p "$(BINDIR)"
	cat aipsetup | sed -e "4{s#AIP_DIR=\"\"#AIP_DIR=\"$(PPWD)\"#}" > "$(BINDIR)/aipsetup"
	chown root.root "$(BINDIR)/aipsetup"
	chmod 755 "$(BINDIR)/aipsetup"
	@echo "<<<[ Sett Up ]>>>"

unsetup:
	-rm "$(BINDIR)/aipsetup"

clean:
	chown -R root.root .
	chmod -R 0600 .
	-rm _*build_*
	-rm *~

release: clean
	echo "$(VERSION)" > ./VERSION
	cd .. ; tar -c ./aipsetup | lzma -9 > "aipsetup-$(VERSION).tar.lzma"
