#!/bin/sh
set -e
set -u

# Based on ypcs' scripts found at:
#     https://github.com/ypcs/vmdebootstrap-vagrant/

CURDIR="$(realpath $(dirname $0))"
ROOT="$1"
[ -z "${ROOT}" ] && echo "E: Missing argument!" && exit 1

mv "${ROOT}/etc/resolv.conf" "${ROOT}/etc/resolv.conf.orig"
cp --dereference /etc/resolv.conf "${ROOT}/etc/resolv.conf"
cp "${CURDIR}/postinstall.sh" "${ROOT}/postinstall.sh"
cp "${CURDIR}/../../../config/chroot_sources/tails.binary.gpg" "${ROOT}/tmp/"
chmod +x "${ROOT}/postinstall.sh"
chroot "${ROOT}" "/postinstall.sh"
rm -f "${ROOT}/postinstall.sh"
mv "${ROOT}/etc/resolv.conf.orig" "${ROOT}/etc/resolv.conf"
