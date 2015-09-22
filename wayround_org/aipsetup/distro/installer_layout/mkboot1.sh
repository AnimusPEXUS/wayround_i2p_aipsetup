#!/bin/bash

set -x 

PPWD=`pwd`
BOOT_D='boot'
BOOT_F='boot_files'

rm -rf $BOOT_D # $BOOT_F
mkdir $BOOT_D $BOOT_F

cd $BOOT_F
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

aipsetup pkg-client get-by-list fi


aipsetup sys-replica maketree `pwd`/../$BOOT_D
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

aipsetup sys install -b=`pwd`/../$BOOT_D *
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

aipsetup sys-clean install-etc -b=`pwd`/../$BOOT_D *
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

cd $PPWD/$BOOT_D/multihost
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

ln -s x86_64-pc-linux-gnu _primary
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

cd $PPWD/$BOOT_D/multihost/x86_64-pc-linux-gnu/src/linux
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi
make clean

cd $PPWD
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

cd $BOOT_D
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

#exit 0
tar -cf ../boot.tar *
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

cd $PPWD

exit 0
