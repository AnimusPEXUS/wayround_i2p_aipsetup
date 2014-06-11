
import glob
import logging
import os.path
import shutil

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'configure', 'build', 'distribute'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        separate_build_dir = False

        source_configure_reldir = 'wpa_supplicant'

        src_dir_p_sep = os.path.join(src_dir, source_configure_reldir)

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                org.wayround.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'configure' in actions and ret == 0:

            t_conf = os.path.join(src_dir_p_sep, '.config')

            shutil.copyfile(
                os.path.join(src_dir_p_sep, 'defconfig'),
                t_conf
                )

            f = open(t_conf, 'a')
            f.write("""
CONFIG_BACKEND=file
CONFIG_CTRL_IFACE=y
CONFIG_DEBUG_FILE=y
CONFIG_DEBUG_SYSLOG=y
CONFIG_DEBUG_SYSLOG_FACILITY=LOG_DAEMON
CONFIG_DRIVER_NL80211=y
CONFIG_DRIVER_WEXT=y
CONFIG_DRIVER_WIRED=y
CONFIG_EAP_GTC=y
CONFIG_EAP_LEAP=y
CONFIG_EAP_MD5=y
CONFIG_EAP_MSCHAPV2=y
CONFIG_EAP_OTP=y
CONFIG_EAP_PEAP=y
CONFIG_EAP_TLS=y
CONFIG_EAP_TTLS=y
CONFIG_IEEE8021X_EAPOL=y
CONFIG_IPV6=y
CONFIG_LIBNL32=y
CONFIG_PEERKEY=y
CONFIG_PKCS12=y
CONFIG_READLINE=y
CONFIG_SMARTCARD=y
CONFIG_WPS=y
CFLAGS += -I/usr/include/libnl3
""")
            f.close()

        if 'build' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[
                    'LIBDIR=/usr/lib',
                    'BINDIR=/usr/bin',
                    'PN531_PATH=/usr/src/nfc'
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'LIBDIR=/usr/lib',
                    'BINDIR=/usr/bin',
                    'PN531_PATH=/usr/src/nfc',
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

            logging.info("Copying manuals")
            os.makedirs(os.path.join(dst_dir, 'usr', 'man', 'man8'))
            os.makedirs(os.path.join(dst_dir, 'usr', 'man', 'man5'))

            m8 = glob.glob(
                os.path.join(src_dir_p_sep, 'doc', 'docbook', '*.8')
                )
            m5 = glob.glob(
                os.path.join(src_dir_p_sep, 'doc', 'docbook', '*.5')
                )

            for i in m8:
                bn = os.path.basename(i)
                shutil.copyfile(
                    i,
                    os.path.join(dst_dir, 'usr', 'man', 'man8', bn)
                    )
                print(i)

            for i in m5:
                bn = os.path.basename(i)
                shutil.copyfile(
                    i,
                    os.path.join(dst_dir, 'usr', 'man', 'man5', bn)
                    )
                print(i)

    return ret
