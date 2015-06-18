
import glob
import logging
import os.path
import shutil

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.source_configure_reldir = 'wpa_supplicant'
        return {
            'src_dir_p_sep': os.path.join(
                self.src_dir,
                self.source_configure_reldir
                )
            }

    def define_actions(self):
        ret = super().define_actions()
        ret['copy_manpages'] = self.builder_action_copy_manpages
        del ret['autogen']
        return ret

    def builder_action_configure(self, called_as, log):

        src_dir_p_sep = self.custom_data['src_dir_p_sep']

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
        return 0

    def builder_action_build(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[
                'LIBDIR=/usr/lib',
                'BINDIR=/usr/bin',
                'PN531_PATH=/usr/src/nfc'
                ],
            arguments=[],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'LIBDIR=/usr/lib',
                'BINDIR=/usr/bin',
                'PN531_PATH=/usr/src/nfc',
                'DESTDIR=' + self.dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_copy_manpages(self, called_as, log):
        log.info("Copying manuals")

        src_dir_p_sep = self.custom_data['src_dir_p_sep']

        os.makedirs(os.path.join(self.dst_dir, 'usr', 'man', 'man8'))
        os.makedirs(os.path.join(self.dst_dir, 'usr', 'man', 'man5'))

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
                os.path.join(self.dst_dir, 'usr', 'man', 'man8', bn)
                )
            log.info("    {}".format(i))

        for i in m5:
            bn = os.path.basename(i)
            shutil.copyfile(
                i,
                os.path.join(self.dst_dir, 'usr', 'man', 'man5', bn)
                )
            log.info("    {}".format(i))
        return 0
