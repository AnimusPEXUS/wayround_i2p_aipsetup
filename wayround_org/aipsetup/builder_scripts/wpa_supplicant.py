
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

        self.apply_host_spec_linking_interpreter_option = False
        self.apply_host_spec_linking_lib_dir_options = False
        self.apply_host_spec_compilers_options = True

        return {
            'src_dir_p_sep': wayround_org.utils.path.join(
                self.get_src_dir(),
                self.source_configure_reldir
                )
            }

    def define_actions(self):
        ret = super().define_actions()
        ret['copy_manpages'] = self.builder_action_copy_manpages
        del ret['autogen']
        del ret['build']
        return ret

    def builder_action_configure(self, called_as, log):

        src_dir_p_sep = self.custom_data['src_dir_p_sep']

        t_conf = wayround_org.utils.path.join(src_dir_p_sep, '.config')

        shutil.copyfile(
            wayround_org.utils.path.join(src_dir_p_sep, 'defconfig'),
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
CFLAGS += -I{hmd}/include/libnl3
{generated}
""".format(hmd=self.calculate_install_prefix(),
           generated='\n'.join(self.all_automatic_flags_as_list())
           )
            )
        f.close()
        return 0

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=[],
            arguments=[
                'all',
                'install',
                'LIBDIR={}'.format(
                    wayround_org.utils.path.join(
                        self.calculate_install_prefix(),
                        'lib'
                        )
                    ),
                'BINDIR={}'.format(
                    wayround_org.utils.path.join(
                        self.calculate_install_prefix(), 'bin'
                        )
                    ),
                'PN531_PATH={}'.format(
                    wayround_org.utils.path.join(
                        self.calculate_install_prefix(), 'src', 'nfc'
                        )
                    ),
                'DESTDIR={}'.format(self.get_dst_dir())
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

        os.makedirs(wayround_org.utils.path.join(
            self.get_dst_host_dir(), 'man', 'man8')
            )
        os.makedirs(wayround_org.utils.path.join(
            self.get_dst_host_dir(), 'man', 'man5')
            )

        m8 = glob.glob(
            wayround_org.utils.path.join(
                src_dir_p_sep,
                'doc',
                'docbook',
                '*.8')
            )
        m5 = glob.glob(
            wayround_org.utils.path.join(
                src_dir_p_sep,
                'doc',
                'docbook',
                '*.5')
            )

        for i in m8:
            bn = os.path.basename(i)
            shutil.copyfile(
                i,
                wayround_org.utils.path.join(
                    self.calculate_dst_install_prefix(),
                    'man',
                    'man8',
                    bn
                    )
                )
            log.info("    {}".format(i))

        for i in m5:
            bn = os.path.basename(i)
            shutil.copyfile(
                i,
                wayround_org.utils.path.join(
                    self.calculate_dst_install_prefix(),
                    'man',
                    'man5',
                    bn)
                )
            log.info("    {}".format(i))
        return 0
