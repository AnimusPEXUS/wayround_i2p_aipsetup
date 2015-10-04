
import os.path
import shutil
import logging
import subprocess
import glob

import wayround_org.utils.path
import wayround_org.utils.file
import wayround_org.utils.checksum


'''
I needed abstraction from aipsetup here, so this uses subprocess.Popen alot,
not direct APIs
'''


def clean_working_dirs(
        boot_d,
        initrd_d, initrd_f,
        root_d, root_f,
        force_packages_download,
        force_packages_reinstall,
        verbose=True
        ):

    # TODO: to deletion
    raise Exception('delete')

    if force_packages_download:
        for i in [initrd_f, root_f]:
            if verbose:
                logging.info("cleaning: {}".format(i))
            shutil.rmtree(i)

    if force_packages_reinstall:
        for i in [initrd_d, root_d]:
            if verbose:
                logging.info("cleaning: {}".format(i))
            shutil.rmtree(i)

    return


def get_packages(list_name, output_dir):

    os.makedirs(output_dir, exist_ok=True)

    p = subprocess.Popen(
        ['aipsetup', 'pkg-client', 'get-by-list', list_name],
        cwd=output_dir
        )
    ret = p.wait()

    return ret


def get_python_packages(python_pkg_dir):
    os.makedirs(python_pkg_dir, exist_ok=True)
    p = subprocess.Popen(
        [
            'python3',
            '-m',
            'pip', 'install', '-d', python_pkg_dir,
            'pip',
            'setuptools',
            'bottle',
            'lxml',
            'mako',
            #'cython',
            'certdata',
            'sqlalchemy',
            # 'aipsetup',
            # 'wayround_org_utils'
            ]
        )
    ret = p.wait()
    return


def check_python_packages(python_pkg_dir):
    """
    return: True - Ok, False - error
    """
    ret = True

    if ret:
        if not os.path.isdir(python_pkg_dir):
            ret = False

    if ret:
        lst = os.listdir(python_pkg_dir)
        for i in [
                'pip',
                'setuptools',
                'bottle',
                'lxml',
                'mako',
                #'cython',
                'certdata',
                'sqlalchemy',
                'aipsetup',
                'wayround_org_utils'
                ]:
            found = False
            for j in lst:
                if j.lower().startswith(i):
                    found = True
                    break

            if not found:
                print("    {} python package not found".format(i))
                ret = False

    return ret


def root_ldconfig(output_dir):
    p = subprocess.Popen(
        [
            'chroot', output_dir,
            '/bin/bash',
            '-c',
            'ldconfig ; exit '
            ]
        )
    ret = p.wait()
    return ret


def install_python_packages(output_dir, python_pkg_dir):

    ret = 0

    target_mont_dir = wayround_org.utils.path.join(
        output_dir,
        'py_pack'
        )

    if not os.path.isdir(python_pkg_dir):
        ret = 1

    if ret == 0:
    
        wayround_org.utils.file.copytree(
            python_pkg_dir, 
            target_mont_dir,
            overwrite_files=False,
            clear_before_copy=True,
            dst_must_be_empty=True,
            verbose=True
            )

    if ret == 0:

        p = subprocess.Popen(
            [
                'chroot', output_dir,
                '/bin/bash',
                '-c',
                """\
python3 -m ensurepip
python3 -m pip install /py_pack/wayround*
#python3 -m pip install /py_pack/MarkupSafe*
#python3 -m pip install /py_pack/certdata*
python3 -m pip install -f /py_pack/ /py_pack/*
exit 0
"""
                ]
            )
        ret = p.wait()

    return ret


def make_root_dirtree(output_dir):

    os.makedirs(output_dir, exist_ok=True)

    p = subprocess.Popen(
        ['aipsetup', 'sys-replica', 'maketree', output_dir],
        cwd=output_dir
        )
    ret = p.wait()

    return ret


def install_packages(packages_dir, output_dir):

    os.makedirs(output_dir, exist_ok=True)

    aips = os.listdir(packages_dir)

    for i in range(len(aips) - 1, -1, -1):
        val = aips[i]
        val_j = wayround_org.utils.path.join(packages_dir, val)

        if not os.path.isfile(val_j) or not val.endswith('.asp'):
            del aips[i]

    ret = 0

    if len(aips) != 0:

        p = subprocess.Popen(
            ['aipsetup', 'sys', 'install', '-b={}'.format(output_dir)] + aips,
            cwd=packages_dir
            )
        ret = p.wait()

    else:
        ret = 1

    return ret


def install_etc(output_dir):

    os.makedirs(output_dir, exist_ok=True)

    p = subprocess.Popen(
        ['aipsetup', 'sys-clean', 'install-etc', '-b={}'.format(output_dir)],
        cwd=output_dir
        )
    ret = p.wait()

    return ret


def make_primary_symlink(output_dir, target_system):
    ret = 0
    try:
        os.symlink(
            target_system,
            wayround_org.utils.path.join(
                output_dir,
                'multihost',
                '_primary'
                )
            )
    except:
        logging.exception('error')
        ret = 1
    return ret


def make_initrd_init(output_dir, boot_part_uuid):
    dirname = wayround_org.utils.path.join(output_dir)
    filename = wayround_org.utils.path.join(dirname, 'init.sh')

    os.makedirs(dirname, exist_ok=True)

    f = open(filename, 'w')
    f.write(
        """\
#!/bin/bash

echo
echo
echo
echo '                                    LAILALO'
echo
echo
echo

#set -x

export LD_LIBRARY_PATH=/lib:/lib64

# this should be already mounted by kernel
# mount -t devtmpfs devtmpfs /dev

mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -o ro PARTUUID={uuid} /boot
mount /boot/root.squash /root_new

# echo "testing overlayfs"
# /bin/bash

# echo "Ignore next 4 possible /root_new/* mount error messages"
# umount /boot

mount --move /boot /root_new/boot

umount /proc
umount /dev
umount /sys

cd /root_new

pivot_root . /root_new/root_old

exec chroot . /init.sh

""".format(
            uuid=boot_part_uuid.lower()
            )
        )
    f.close()

    p = subprocess.Popen(['chmod', '+x', filename])
    p.wait()

    return 0


def make_root_init(output_dir, boot_part_uuid):
    dirname = wayround_org.utils.path.join(output_dir)
    filename = wayround_org.utils.path.join(dirname, 'init.sh')

    os.makedirs(dirname, exist_ok=True)

    f = open(filename, 'w')
    f.write(
        """\
#!/bin/bash

# set -x

umount /root_old

mount -t tmpfs tmpfs /overlay

mkdir /overlay/upper
mkdir /overlay/work

mount -t overlay overlay \
-olowerdir=/,upperdir=/overlay/upper,workdir=/overlay/work /overlay_merged

mount --move /boot /overlay_merged/boot

exec chroot /overlay_merged /init_merged.sh

""".format(
            uuid=boot_part_uuid.lower()
            ))
    f.close()

    p = subprocess.Popen(['chmod', '+x', filename])
    p.wait()

    return 0

def make_root_init_merged(output_dir, boot_part_uuid):
    dirname = wayround_org.utils.path.join(output_dir)
    filename = wayround_org.utils.path.join(dirname, 'init_merged.sh')

    os.makedirs(dirname, exist_ok=True)

    f = open(filename, 'w')
    f.write(
        """\
#!/bin/bash

# set -x

mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev
# mount -o ro PARTUUID={uuid} /boot

echo "---------------------------------------------------------------"
echo "Wellcome into Lailalo GNU/Linux distribution installation shell"
echo "----------------------------------[special agent's distro ;-)]-"
echo ''
echo "This is currently a development build - expect problems"
echo ''

exec /bin/bash

""".format(
            uuid=boot_part_uuid.lower()
            ))
    f.close()

    p = subprocess.Popen(['chmod', '+x', filename])
    p.wait()

    return 0


def clean_linux_source(output_dir):

    ret = 0

    dirname = wayround_org.utils.path.join(
        output_dir,
        'multihost',
        '_primary',
        'src',
        'linux'
        )

    if os.path.isdir(dirname):

        p = subprocess.Popen(['make', 'clean'], cwd=dirname)
        ret = p.wait()

    return ret


def make_boot_dir(boot_d, root_d):
    ret = 0

    os.makedirs(boot_d, exist_ok=True)

    src_dir = wayround_org.utils.path.join(
        root_d,
        'boot'
        )

    lst = os.listdir(src_dir)

    for i in lst:
        sj = wayround_org.utils.path.join(src_dir, i)
        bj = wayround_org.utils.path.join(boot_d, i)

        if os.path.isfile(bj):
            os.unlink(bj)

        os.link(sj, bj)

    return ret


def squash_dir(dirname, outfile, opts):
    p = subprocess.Popen(['mksquashfs', dirname, outfile] + opts)
    ret = p.wait()
    return ret


def compress_file(dirname, filename, comp, opts):
    p = subprocess.Popen([comp] + opts + [filename], cwd=dirname)
    ret = p.wait()
    return ret


def make_extlinux_conf(
        output_dir,
        linux_file_name,
        ramdisk_size
        ):

    linux_file_name = 'vmlinuz-4.2.1-x86_64-pc-linux-gnu'
    ramdisk_size = 102400

    dirname = wayround_org.utils.path.join(output_dir, 'extlinux')
    filename = wayround_org.utils.path.join(dirname, 'extlinux.conf')

    os.makedirs(dirname, exist_ok=True)

    f = open(filename, 'w')
    f.write(
        """\
UI menu.c32

DEFAULT normal
PROMPT 1
TIMEOUT 50


LABEL Lailalo GNU/Linux distribution installation shell
    LINUX /{linux_file_name}
    APPEND root=/dev/ram0 vga=0x318 init=/init.sh initrd=/initrd.squash.gz \
ramdisk_size={ramdisk_size} ro

""".format(
            linux_file_name=linux_file_name,
            ramdisk_size=ramdisk_size
            )
        )
    f.close()

    p = subprocess.Popen(['chmod', '+x', filename])
    p.wait()

    return 0


def smart_redo_aips_dirs(
        initrd_f, initrd_d,
        root_f, root_d
        ):
    for i in [
            (initrd_f, initrd_d),
            (root_f, root_d),
            ]:

        if wayround_org.utils.checksum.is_dir_changed(
                i[0],
                i[0] + '.sha512',
                verbose=True
                ):
            if os.path.exists(i[1]):
                wayround_org.utils.file.remove_if_exists(i[1])
    return


def smart_redo_d_dirs(
        initrd_d, initrd_squash,
        root_d, root_squash,
        snap_d, snap_squash
        ):
    for i in [
            (initrd_d, initrd_squash),
            (root_d, root_squash),
            (snap_d, snap_squash)
            ]:

        if wayround_org.utils.checksum.is_dir_changed(
                i[0],
                i[0] + '.sha512',
                verbose=True
                ):
            if os.path.exists(i[1]):
                wayround_org.utils.file.remove_if_exists(i[1])
    return


def smart_redo(
        working_dir,
        boot_d,
        boot_tar,
        root_d,
        root_f,
        initrd_d,
        initrd_f,
        initrd_d_init_sh,
        root_d_init_sh,
        snap_d,
        mnt_d,
        initrd_squash,
        initrd_squash_comp,
        root_squash,
        dst_initrd_squash_comp,
        dst_root_squash,
        snap_squash,
        mnt_extlinux_path,
        boot_img
        ):

    anything_removed = True
    while anything_removed:
        anything_removed = False
        for i in [
                (initrd_f, initrd_d),
                (root_f, root_d),

                (initrd_squash_comp, dst_initrd_squash_comp),

                (root_d, root_squash),
                (initrd_d, initrd_squash),

                (initrd_d_init_sh, initrd_squash),
                (root_d_init_sh, root_squash),

                (root_squash, boot_d),
                (initrd_squash, boot_d),

                (initrd_squash, initrd_squash_comp),
                (initrd_squash_comp, boot_d),

                (dst_initrd_squash_comp, boot_tar),
                (dst_root_squash, boot_tar),

                (boot_d, boot_tar),
                (boot_tar, boot_img),

                ]:

            if not os.path.exists(i[0]):
                if os.path.exists(i[1]):
                    anything_removed = True
                    logging.info(
                        "    {} not exists, so removing also {}".format(
                            i[0], i[1]
                            )
                        )
                wayround_org.utils.file.remove_if_exists(i[1])

    return


def create_flashdrive_image(
        working_dir,
        force_packages_download=False,
        force_packages_reinstall=False,
        force_snap_image_rebuild=False,
        force_root_image_rebuild=False,
        force_initrd_image_rebuild=False,
        target_system='x86_64-pc-linux-gnu'
        ):

    image_size = '9GiB'  # value for fallocate command

    boot_partition_uuid = '5A44A96C-37FF-4E15-A9B5-A7275C3B98A3'

    initrd_final_compressor = 'gzip'
    initrd_final_compressor_ext = '.gz'
    initrd_final_compressor_options = ['-9k']

    working_dir = wayround_org.utils.path.abspath(working_dir)

    os.makedirs(working_dir, exist_ok=True)

    python_pkg_dir = wayround_org.utils.path.join(working_dir, 'py_packs')

    boot_d = wayround_org.utils.path.join(working_dir, 'boot')
    boot_tar = wayround_org.utils.path.join(working_dir, 'boot.tar')

    initrd_d = wayround_org.utils.path.join(working_dir, 'initrd')
    initrd_f = wayround_org.utils.path.join(working_dir, 'initrd_aips')

    root_d = wayround_org.utils.path.join(working_dir, 'root')
    root_f = wayround_org.utils.path.join(working_dir, 'root_aips')

    snap_d = wayround_org.utils.path.join(working_dir, 'snap')

    initrd_d_init_sh = wayround_org.utils.path.join(initrd_d, 'init.sh')
    root_d_init_sh = wayround_org.utils.path.join(root_d, 'init.sh')

    mnt_d = wayround_org.utils.path.join(working_dir, 'mnt')

    squash_params = ['-comp', 'xz', '-no-exports', '-all-root']

    initrd_squash = wayround_org.utils.path.join(working_dir, 'initrd.squash')
    initrd_squash_comp = initrd_squash + initrd_final_compressor_ext
    root_squash = wayround_org.utils.path.join(working_dir, 'root.squash')

    snap_squash = wayround_org.utils.path.join(working_dir, 'snap.squash')

    dst_initrd_squash_comp = wayround_org.utils.path.join(
        boot_d,
        'initrd.squash' + initrd_final_compressor_ext
        )
    dst_root_squash = wayround_org.utils.path.join(boot_d, 'root.squash')
    dst_snap_squash = wayround_org.utils.path.join(boot_d, 'snap.squash')

    loop_dev_name = 'loop0'
    loop_dev_path = wayround_org.utils.path.join('/dev', loop_dev_name)
    loop_dev_part1_name = loop_dev_path + 'p1'

    boot_img = wayround_org.utils.path.join(working_dir, 'boot.bin')

    mnt_extlinux_path = wayround_org.utils.path.join(mnt_d, "extlinux")

    # == here starts real actions

    get_python_packages(python_pkg_dir)

    if not check_python_packages(python_pkg_dir):
        raise Exception(
            "provide {} dir with required python packages".format(
                python_pkg_dir
                )
            )

    smart_redo(
        working_dir,
        boot_d,
        boot_tar,
        root_d,
        root_f,
        initrd_d,
        initrd_f,
        initrd_d_init_sh,
        root_d_init_sh,
        snap_d,
        mnt_d,
        initrd_squash,
        initrd_squash_comp,
        root_squash,
        dst_initrd_squash_comp,
        dst_root_squash,
        snap_squash,
        mnt_extlinux_path,
        boot_img
        )

    ret = 0

    if not isinstance(initrd_final_compressor_options, list):
        initrd_final_compressor_options = [initrd_final_compressor_options]

    # TODO: at the time of coding this (26 sep 2015), both of those are
    #       returning non-zero. it's normal as for "distro under construction".
    #       but it must be fixed and return values must be taken into account
    get_packages('fib', initrd_f)
    get_packages('fi', root_f)

    smart_redo_aips_dirs(
        initrd_f, initrd_d,
        root_f, root_d
        )

    # TODO: same as for get_packages() functions

    if not os.path.isdir(initrd_d):
        make_root_dirtree(initrd_d)
        install_packages(initrd_f, initrd_d)
        # install_etc(initrd_d)
        make_primary_symlink(initrd_d, target_system)

    if not os.path.isdir(root_d):
        make_root_dirtree(root_d)
        install_packages(root_f, root_d)
        make_primary_symlink(root_d, target_system)
        clean_linux_source(root_d)

    install_etc(root_d)

    os.makedirs(
        wayround_org.utils.path.join(initrd_d, 'root_new'),
        exist_ok=True
        )

    #os.makedirs(
    #    wayround_org.utils.path.join(initrd_d, 'root_new_ro'),
    #    exist_ok=True
    #    )

    os.makedirs(
        wayround_org.utils.path.join(root_d, 'root_old'),
        exist_ok=True
        )
    os.makedirs(
        wayround_org.utils.path.join(root_d, 'snap'),
        exist_ok=True
        )

    os.makedirs(
        wayround_org.utils.path.join(root_d, 'overlay'),
        exist_ok=True
        )

    os.makedirs(
        wayround_org.utils.path.join(root_d, 'overlay_merged'),
        exist_ok=True
        )

    root_ldconfig(root_d)

    install_python_packages(root_d, python_pkg_dir)

    make_initrd_init(initrd_d, boot_partition_uuid)
    make_root_init(root_d, boot_partition_uuid)
    make_root_init_merged(root_d, boot_partition_uuid)

    smart_redo_d_dirs(
        initrd_d, initrd_squash,
        root_d, root_squash,
        snap_d, snap_squash
        )

    smart_redo(
        working_dir,
        boot_d,
        boot_tar,
        root_d,
        root_f,
        initrd_d,
        initrd_f,
        initrd_d_init_sh,
        root_d_init_sh,
        snap_d,
        mnt_d,
        initrd_squash,
        initrd_squash_comp,
        root_squash,
        dst_initrd_squash_comp,
        dst_root_squash,
        snap_squash,
        mnt_extlinux_path,
        boot_img
        )

    # == root ==

    make_boot_dir(boot_d, root_d)

    if force_root_image_rebuild:
        if os.path.isfile(root_squash):
            os.unlink(root_squash)

    if not os.path.isfile(root_squash):
        squash_dir(root_d, root_squash, squash_params)

    # == initrd ==

    # if os.path.isfile(initrd_squash):
    #    os.unlink(initrd_squash)

    if force_initrd_image_rebuild:
        if os.path.isfile(initrd_squash_comp):
            os.unlink(initrd_squash_comp)

        if os.path.isfile(initrd_squash):
            os.unlink(initrd_squash)

    if not os.path.isfile(initrd_squash_comp):
        squash_dir(initrd_d, initrd_squash, squash_params)
        compress_file(
            working_dir,
            initrd_squash,
            initrd_final_compressor,
            initrd_final_compressor_options
            )
        # if os.path.isfile(initrd_squash):
        #    os.unlink(initrd_squash)

    initrd_squash_size_kb = int(os.stat(initrd_squash).st_size / 1024) + 1
    #print("initrd_squash_size_kb: {}".format(initrd_squash_size_kb))

    # == snap ==

    if not os.path.isdir(snap_d):
        raise Exception(
            "provide {} dir".format(snap_d)
            )

    if force_snap_image_rebuild:
        if os.path.isfile(snap_squash):
            os.unlink(snap_squash)

    if not os.path.isfile(snap_squash):
        squash_dir(snap_d, snap_squash, squash_params)

    # ====

    if os.path.isfile(dst_initrd_squash_comp):
        os.unlink(dst_initrd_squash_comp)

    if os.path.isfile(dst_root_squash):
        os.unlink(dst_root_squash)

    if os.path.isfile(dst_snap_squash):
        os.unlink(dst_snap_squash)

    os.link(initrd_squash_comp, dst_initrd_squash_comp)
    os.link(root_squash, dst_root_squash)
    os.link(snap_squash, dst_snap_squash)

    if not os.path.isfile(boot_tar):
        lst = os.listdir(boot_d)
        p = subprocess.Popen(['tar', '-cvf', boot_tar] + lst, cwd=boot_d)
        res = p.wait()
        if res != 0:
            raise Exception('tar -cvf')

    p = subprocess.Popen(['umount', loop_dev_part1_name])
    p.wait()

    p = subprocess.Popen(['partx', '-d', loop_dev_path])
    p.wait()

    p = subprocess.Popen(['losetup', '-d', loop_dev_path])
    p.wait()

    if os.path.isfile(boot_img):
        os.unlink(boot_img)

    if not os.path.isfile(boot_img):
        p = subprocess.Popen(['fallocate', '-l', image_size, boot_img])
        res = p.wait()
        if res != 0:
            raise Exception('fallocate')

    p = subprocess.Popen(['losetup', loop_dev_path, boot_img])
    res = p.wait()
    if res != 0:
        raise Exception('losetup')

    sfdisk_cmd = """\
label: gpt
device: {loop_dev_path}
unit: sectors

{loop_dev_part1_name} : type=21686148-6449-6E6F-744E-656564454649, \
uuid={boot_partition_uuid}, attrs="LegacyBIOSBootable"
""".format(
        loop_dev_path=loop_dev_path,
        loop_dev_part1_name=loop_dev_part1_name,
        boot_partition_uuid=boot_partition_uuid
        )

    p = subprocess.Popen(['sfdisk', loop_dev_path], stdin=subprocess.PIPE)
    p.communicate(bytes(sfdisk_cmd, 'utf-8'))
    res = p.wait()
    if res != 0:
        raise Exception('sfdisk')

    p = subprocess.Popen(['partx', '-a', loop_dev_path])
    res = p.wait()
    if res != 0:
        raise Exception('partx')

    p = subprocess.Popen(['mke2fs', loop_dev_part1_name])
    res = p.wait()
    if res != 0:
        raise Exception('mke2fs')

    os.makedirs(mnt_d, exist_ok=True)

    p = subprocess.Popen(['mount', loop_dev_part1_name, mnt_d])
    res = p.wait()
    if res != 0:
        raise Exception('mount')

    p = subprocess.Popen(
        [
            'tar', '-xf', boot_tar, '--no-same-owner', '-C', mnt_d
            ]
        )
    res = p.wait()
    if res != 0:
        raise Exception('tar')

    os.makedirs(mnt_extlinux_path, exist_ok=True)

    res = wayround_org.utils.file.copytree(
        '/usr/share/syslinux',  # TODO: no hard code
        mnt_extlinux_path,
        overwrite_files=True,
        clear_before_copy=False,
        dst_must_be_empty=True,
        verbose=False
        )
    if res != 0:
        raise Exception('/usr/share/syslinux')  # TODO: no hard code

    p = subprocess.Popen(['extlinux', '--install', mnt_extlinux_path])
    res = p.wait()
    if res != 0:
        raise Exception('extlinux')

    # TODO: no hard code
    with open('/usr/share/syslinux/gptmbr.bin', 'br') as f:
        with open(loop_dev_path, 'wb') as f2:
            f2.seek(0)
            f2.write(f.read())

    linux_file_name = glob.glob(
        wayround_org.utils.path.join(
            mnt_d,
            'vmlinuz-*'
            )
        )

    if len(linux_file_name) != 1:
        raise Exception(
            "vmlinuz-* file count != 1 ({})".format(len(linux_file_name))
            )

    linux_file_name = os.path.basename(linux_file_name[0])

    res = make_extlinux_conf(
        mnt_d,
        linux_file_name=linux_file_name,
        ramdisk_size=initrd_squash_size_kb
        )
    if res != 0:
        raise Exception('extlinux conf')

    p = subprocess.Popen(['umount', loop_dev_part1_name])
    p.wait()

    p = subprocess.Popen(['partx', '-d', loop_dev_path])
    p.wait()

    p = subprocess.Popen(['losetup', '-d', loop_dev_path])
    p.wait()

    print(
        """
------------------------------------------------------------------------------
Summary:
    Target Flash Drive Image Size: {image_size}
    GPT Boot Partition UUID: {boot_partition_uuid}
    Compressor For initrd: {initrd_final_compressor}
    Compressor Options: {initrd_final_compressor_options}
    Working in Directory: {working_dir}
    Directory For Boot Partition Files: {boot_d}
    Boot Partition tar Named: {boot_tar}
    initrd Formation Directory: {initrd_d}
    Directory With Downloaded initrd Packages: {initrd_f}
    root File System Formation Directory: {root_d}
    Directory With Downloaded root File System Packages: {root_f}
    Working Mount Dir for editing boot partition: {mnt_d}
    squashfs Compression Parameters: {squash_params}
    Name for initrd squashfs: {initrd_squash}
    Name for compressed initrd squashfs: {initrd_squash_comp}
    Name for root squashfs: {root_squash}
    Name for squashed initrd under boot directory: {dst_initrd_squash_comp}
    Name for squashed root under boot directory: {dst_root_squash}
    Working loop device name: {loop_dev_name}
    Full loop dev path: {loop_dev_path}
    Full loop dev partition path: {loop_dev_part1_name}
    extlinux installation directory: {mnt_extlinux_path}

    Boot image saving name is: {boot_img}
""".format(
            image_size=image_size,
            boot_partition_uuid=boot_partition_uuid,
            initrd_final_compressor=initrd_final_compressor,
            initrd_final_compressor_options=initrd_final_compressor_options,
            working_dir=working_dir,
            boot_d=boot_d,
            boot_tar=boot_tar,
            root_d=root_d,
            root_f=root_f,
            initrd_d=initrd_d,
            initrd_f=initrd_f,
            mnt_d=mnt_d,
            squash_params=squash_params,
            initrd_squash=initrd_squash,
            initrd_squash_comp=initrd_squash_comp,
            root_squash=root_squash,
            dst_initrd_squash_comp=dst_initrd_squash_comp,
            dst_root_squash=dst_root_squash,
            loop_dev_name=loop_dev_name,
            loop_dev_path=loop_dev_path,
            loop_dev_part1_name=loop_dev_part1_name,
            mnt_extlinux_path=mnt_extlinux_path,
            boot_img=boot_img
            )
        )

    return ret
