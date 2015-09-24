#!/bin/bash

#set -x

PPWD=`pwd`
BOOT_D="$PPWD/boot"
BOOT_F="$PPWD/boot_aips"
ROOT_D="$PPWD/root"
ROOT_F="$PPWD/root_aips"
ROOT_SQUASH="$PPWD/root.squash"
BOOT_TAR="$PPWD/boot.tar"

install_dir_files_dir=
install_dir_target_dir=
install_dir_aipsetup_group_list_name=
install_dir_echo_title=
install_dir() {

cd "$install_dir_files_dir"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

echo "Downloading $install_dir_echo_title files"
aipsetup pkg-client get-by-list $install_dir_aipsetup_group_list_name

cd "$install_dir_files_dir"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

echo "Making new $install_dir_echo_title directory tree"
aipsetup sys-replica maketree "$install_dir_target_dir"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

echo "Installing $install_dir_echo_title packages"
aipsetup sys install -b="$install_dir_target_dir" *
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

echo "Installing /etc files"
aipsetup sys-clean install-etc -b="$install_dir_target_dir" *
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

echo "Creating /multihost/_primary link"
cd "$install_dir_target_dir/multihost"
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

}

echo "Cleaning working dirs"
rm -vrf "$BOOT_D" "$BOOT_F" "$ROOT_D" "$ROOT_F"
mkdir -pv "$BOOT_D" "$BOOT_F" "$ROOT_D" "$ROOT_F"

install_dir_files_dir="$BOOT_F"
install_dir_target_dir="$BOOT_D"
install_dir_aipsetup_group_list_name=fib
install_dir_echo_title=boot
install_dir

install_dir_files_dir="$ROOT_F"
install_dir_target_dir="$ROOT_D"
install_dir_aipsetup_group_list_name=fi
install_dir_echo_title=root
install_dir

echo "Cleaning linux src dir"
cd "$ROOT_D/multihost/x86_64-pc-linux-gnu/src/linux"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi
make clean

cd "$PPWD"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

echo "Moving /boot dir to separate location"

mv -v "$ROOT_D/boot" "$BOOT_D"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

echo "Squashing new root fs"
rm -v "$ROOT_SQUASH"
mksquashfs "$ROOT_D" "$ROOT_SQUASH" -comp xz -no-exports -no-xattrs -all-root
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

echo "Moving root.squash into boot dir"

mv -v "$ROOT_SQUASH" "$BOOT_D"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

echo "Creating additional needed files in boot dir"

mkdir -p "$BOOT_D/root_mnt"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

echo "Creating tar with boot fs"

cd "$BOOT_D"
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

tar -vcf "$BOOT_TAR" *
if [ $? -ne 0 ]
then
    echo error
    exit 1
fi

cd "$PPWD"


exit 0
