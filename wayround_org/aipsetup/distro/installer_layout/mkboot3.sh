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

umount $MNT_DIR
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

partx -d $LOOP_D
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

losetup -d $LOOP_D

