#!/bin/bash

set -x 

PPWD=`pwd`
BOOT_D="$PPWD/boot"
BOOT_F="$PPWD/boot_aips"
ROOT_D="$PPWD/root"
ROOT_F="$PPWD/root_aips"
ROOT_SQUASH="$PPWD/root.squash"
BOOT_TAR="$PPWD/boot.tar"
MNT_DIR="$PPWD/mnt"

BOOT_MBR="$PPWD/boot.mbr"
LOOP='loop0'
LOOP_D='/dev/'$LOOP
LOOP_DP="$LOOP_D"p1
EXTLINUX_DIR="$MNT_DIR/boot/extlinux"

umount "$MNT_DIR"

partx -d "$LOOP_D"

losetup -d "$LOOP_D"

# target is 8GB flash drive (note: not GiB - GB. man dd)
dd if=/dev/zero of=$BOOT_MBR bs=1MB count=8000

#dd if=/dev/zero of="$LOOP_D" bs=1M count=10

if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

losetup "$LOOP_D" "$BOOT_MBR" 
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi


sfdisk "$LOOP_D" <<EOF
label: gpt
device: $LOOP_D
unit: sectors

$LOOP_DP : type=21686148-6449-6E6F-744E-656564454649, uuid=5A44A96C-37FF-4E15-A9B5-A7275C3B98A3, attrs="LegacyBIOSBootable"
EOF

if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

partx -a "$LOOP_D"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

mke2fs "$LOOP_DP"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

mkdir -p "$MNT_DIR"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

mount "$LOOP_DP" "$MNT_DIR"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

tar -xf "$BOOT_TAR" --no-same-owner -C "$MNT_DIR"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

mkdir -p "$EXTLINUX_DIR"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

cd "$EXTLINUX_DIR"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

cp -r /usr/share/syslinux/* .
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

cat /usr/share/syslinux/gptmbr.bin > "$LOOP_D"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

extlinux --install .
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

cat > ./extlinux.conf <<EOF
UI menu.c32

DEFAULT normal
PROMPT 1
TIMEOUT 50


LABEL normal
    LINUX /boot/vmlinuz-4.2.1-x86_64-pc-linux-gnu
    APPEND root=PARTUUID=5A44A96C-37FF-4E15-A9B5-A7275C3B98A3 vga=0x318 init=/bin/bash ro

EOF

cd "$PPWD"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

exit 0
