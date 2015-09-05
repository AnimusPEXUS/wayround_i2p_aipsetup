
import pprint

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.aipsetup.builder_scripts.std_cmake
import wayround_org.aipsetup.buildtools.autotools as autotools


class Builder(wayround_org.aipsetup.builder_scripts.std_cmake.Builder):

    def define_custom_data(self):
        self.apply_host_spec_compilers_options = True
        return

    def calculate_compilers_options(self, d):
        super().calculate_compilers_options(d)

        if not 'CC' in d:
            d['CC'] = []
        d['CC'].append(self.calculate_CC_string())

        if not 'CXX' in d:
            d['CXX'] = []
        d['CXX'].append(self.calculate_CXX_string())

        return

    def builder_action_configure_define_environment(self, called_as, log):

        std_cmake_opts = super().builder_action_configure_define_opts(
            called_as,
            log
            )

        std_cmake_opts_dict = {}
        for i in std_cmake_opts:
            splitted = i.split('=', 1)
            key = splitted[0][2:]
            value = splitted[1]

            std_cmake_opts_dict[key] = value

        ret = {}

        # print("std_env0: {}".format(std_cmake_opts_dict))

        # print(
        #    "std_env: {}".format(
        #        wayround_org.aipsetup.builder_scripts.std.Builder.\
        #        all_automatic_flags_as_dict(self)
        #        )
        #    )

        ret.update(self.all_automatic_flags_as_dict())
        ret.update(
            wayround_org.aipsetup.builder_scripts.std.Builder.
            all_automatic_flags_as_dict(
                self
                )
            )
        ret.update(std_cmake_opts_dict)

        log.info("Calculated environment:\n{}".format(pprint.pformat(ret)))

        return ret

    def builder_action_configure_define_opts(self, called_as, log):

        std_opts = wayround_org.aipsetup.builder_scripts.std.Builder.\
            builder_action_configure_define_opts(
                self,
                called_as,
                log
                )

        for i in range(len(std_opts) - 1, -1, -1):
            for j in [
                    '--datarootdir=',
                    '--datadir=',
                    '--mandir=',
                    '--libexecdir=',
                    '--bindir=',
                    '--sbindir=',
                    '--includedir=',
                    '--libdir=',
                    '--sysconfdir=',
                    '--localstatedir=',
                    '--enable-shared',
                    '--host=',
                    '--build=',
                    '--with-sysroot=',
                    'CC=',
                    'GCC=',
                    'CXX=',
                    'CMAKE_CXX_COMPILER=',
                    'CMAKE_C_COMPILER=',
                    'CMAKE_CXX_FLAGS=',
                    'CMAKE_C_FLAGS=',
                    ]:
                if std_opts[i].startswith(j):
                    del std_opts[i]
                    break

        std_cmake_opts = super().builder_action_configure_define_opts(
            called_as,
            log
            )

        for i in range(len(std_cmake_opts) - 1, -1, -1):
            for j in [
                    '-DCC=',
                    '-DCXX=',
                    ]:
                if std_cmake_opts[i].startswith(j):
                    del std_cmake_opts[i]
                    break

        ret = [
            '--no-qt-gui',
            ]

        ret += std_opts

        ret += [
            '--',
            '-DCURSES_INCLUDE_PATH={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'include',
                    'ncursesw'
                    )
                ),
            #'-DCURSES_INCLUDE_DIRS={}'.format(
            #    wayround_org.utils.path.join(
            #        self.calculate_install_prefix(),
            #        'include',
            #        'ncursesw'
            #        )
            #    )
            ]

        ret += std_cmake_opts

        return ret

    builder_action_configure = \
        wayround_org.aipsetup.builder_scripts.std.Builder.\
        builder_action_configure

    def builder_action_build_define_args(self, called_as, log):
        ret = super().builder_action_build_define_args(called_as, log)
        ret += ['VERBOSE=1']
        return ret
