#!/usr/bin/make -f

.PHONY: deb

deb:
	videb debian.yml create

install: deb
	if [$EUID -ne 0]
		then echo "You must be root to install this package"
		exit 1
	fi
	dpkg -i *.deb
