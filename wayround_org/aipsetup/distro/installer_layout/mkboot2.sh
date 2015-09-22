#!/bin/bash

set -x 

PPWD=`pwd`
BOOT_D='boot'
BOOT_F='boot_files'
LOOP='loop0'
LOOP_D='/dev/'$LOOP
LOOP_DP="$LOOP_D"p1
MNT_DIR="$PPWD/mnt"
EXTLINUX_DIR="$MNT_DIR/boot/extlinux"

# target is 8GiB flash drive
#dd if=/dev/zero of=./boot.mbr bs=1M count=7500

umount $MNT_DIR

losetup -d $LOOP_D
losetup $LOOP_D ./boot.mbr 
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

partx -d $LOOP_D

sfdisk $LOOP_D <<EOF
label: dos
device: $LOOP_D
unit: sectors

$LOOP_DP : type=83, bootable
EOF

if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

partx -a $LOOP_D
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

mke2fs $LOOP_DP
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

mkdir -p $MNT_DIR
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

mount $LOOP_DP $MNT_DIR
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

tar -xf ./boot.tar --no-same-owner -C $MNT_DIR
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

mkdir -p $EXTLINUX_DIR
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

cd $EXTLINUX_DIR
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

cat /usr/share/syslinux/mbr.bin > $LOOP_D
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

cd $PPWD
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi
