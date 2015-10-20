

import os.path
import wayround_org.utils.path
import wayround_org.utils.pkgconfig
import wayround_org.utils.file
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std
import wayround_org.aipsetup.builder_scripts.qemu


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        ret = {
            'qemu_builder': wayround_org.aipsetup.builder_scripts.qemu.Builder(
                self.control
                )
            }
        return ret

    def builder_action_configure_define_opts(self, called_as, log):

        qemu_builder = self.custom_data['qemu_builder']

        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--with-system-qemu={}'.format(
                wayround_org.utils.file.which(
                    'qemu-system-x86_64'
                    )
                ),
            '--with-extra-qemuu-configure-args={}'.format(
                ' '.join(
                    qemu_builder.builder_action_configure_define_opts(
                        'configure',
                        log
                        )
                    )
                ),
            'CFLAGS=-g -O3 {}'.format(
                wayround_org.utils.pkgconfig.pkgconfig('ncurses', '--cflags')
                )
            ]

        return ret

    def builder_action_build_define_opts(self, called_as, log):

        qemu_builder = self.custom_data['qemu_builder']

        ret = super().builder_action_build_define_opts(called_as, log)

        ret += [
            'EXTRA_CFLAGS_XEN_TOOLS={}'.format(
                wayround_org.utils.pkgconfig.pkgconfig_include('ncurses')
                ),
            #'EXTRA_CFLAGS_QEMU_TRADITIONAL={}'.format(
            #    qemu_builder.all_automatic_flags_as_dict()
            #    ),
            #'EXTRA_CFLAGS_QEMU_XEN={}'.format(
            #    qemu_builder.all_automatic_flags_as_dict()
            #    ),
            'CURSES_LIBS={}'.format(
                wayround_org.utils.pkgconfig.pkgconfig('ncurses', '--libs')
                ),
            ]

        return ret

    # temporary for debugging
    def builder_action_build_define_cpu_count(self, called_as, log):
        return 1
