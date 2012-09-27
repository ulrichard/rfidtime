#!/bin/sh
# build a debian sourcepackage and upload it to the launchpad ppa

rm -rf build
rm -rf build-*
rm *-stamp
rm -rf debian/build*
rm -rf debian/tmp
rm -rf debian/rfidtime/
rm -rf debian/rfidtime-alix/
rm -rf debian/rfidtime-bifferboard/
rm debian/*.log
rm debian/*.debhelper
rm debian/*.substvars
rm debian/files
rm debian/substvars

:${VERSIONNBR:=$(parsechangelog | grep Version | sed -e "s/Version: //g" -e "s/\\~.*//g")}

for DISTRIBUTION in quantal precise #oneiric  
do
	sed -i  -e "s/oneiric/${DISTRIBUTION}/g" -e "s/precise/${DISTRIBUTION}/g" -e "s/quantal/${DISTRIBUTION}/g" debian/changelog
	dpkg-buildpackage -rfakeroot -k${GPGKEY} -S
	dput ppa:richi-paraeasy/ppa ../rfidtime_${VERSIONNBR}~${DISTRIBUTION}_source.changes
done
