
import logging
import os.path
import subprocess
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


import wayround_org.aipsetup.builder_scripts.std


class Builder_wow64(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        self.separate_build_dir = wayround_org.utils.path.join(
            self.get_src_dir(),
            'wine64'
            )
        # self.source_configure_reldir = '..'

        '''
        self.total_host_redefinition = 'x86_64-pc-linux-gnu'
        self.total_build_redefinition = 'x86_64-pc-linux-gnu'
        self.total_target_redefinition = 'x86_64-pc-linux-gnu'
        '''

        return None

    def define_actions(self):

        t = wayround_org.aipsetup.builder_scripts.std.Builder.define_actions(
            self
            )

        # t2 = Builder.define_actions(
        #    self
        #    )

        ret = collections.OrderedDict()
        ret['configure'] = t['configure']
        ret['build'] = t['build']
        ret['distribute'] = t['distribute']

        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--enable-win64',
            #'CFLAGS=-O2 -fno-builtin-memcpy'
            ]
        return ret

    def builder_action_configure(self, called_as, log):
        os.makedirs(
            wayround_org.utils.path.join(
                self.get_src_dir(),
                'wine64'
                ),
            exist_ok=True
            )
        ret = super().builder_action_configure(called_as, log)
        return ret

    # def builder_action_configure_define_environment


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        self.separate_build_dir = wayround_org.utils.path.join(
            self.get_src_dir(),
            'wine32'
            )

        ret = {
            'Builder_wow64': None,
            #'wow64': False
            }

        # if self.get_arch_from_pkgi().startswith('i686'):
        if self.get_arch_from_pkgi().startswith('x86_64'):
            ret['Builder_wow64'] = Builder_wow64(self.control)

            '''
            if wayround_org.utils.file.which(
                    'x86_64-pc-linux-gnu-gcc',
                    '/multiarch/x86_64-pc-linux-gnu'
                    ) != None:
                print("""\
---------
configured for i686
but x86_64 GCC was found too
so going to build with Wow64 support
---------
""")
                ret['Builder_wow64'] = Builder_wow64(self.control)
                # ret['wow64'] = True
            '''

        return ret

    def define_actions(self):

        if self.custom_data['Builder_wow64'] is not None:

            b64_actions = self.custom_data['Builder_wow64'].define_actions()

        ret_l = [
            ('src_cleanup', self.builder_action_src_cleanup),
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('extract', self.builder_action_extract),
            ('patch', self.builder_action_patch),
            ('autogen', self.builder_action_autogen)]

        if self.custom_data['Builder_wow64'] is not None:

            ret_l += [
                ('configure_wow64', b64_actions['configure']),
                ('build_wow64', b64_actions['build']),
                #('distribute_wow64', b64_actions['distribute']),
                ]

        ret_l += [
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ]

        if self.custom_data['Builder_wow64'] is not None:

            ret_l += [
                ('distribute_wow64', b64_actions['distribute'])
                ]

        ret = collections.OrderedDict(ret_l)
        return ret

    def _reconfigure_arch(self):

        def get_arch_from_pkgi():
            return 'i686-pc-linux-gnu'

        def get_multilib_variants_from_pkgi():
            return ['m32']

        self.get_arch_from_pkgi = get_arch_from_pkgi
        self.get_multilib_variants_from_pkgi = get_multilib_variants_from_pkgi
        return

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(called_as, log)
        if self.custom_data['Builder_wow64'] is not None:

            ret += [
                '--with-wine64={}'.format(
                    wayround_org.utils.path.join(self.get_src_dir(), 'wine64')
                    )
                ]

        ret += [
            #'--prefix={}'.format(
            #    '/multihost/x86_64-pc-linux-gnu/multiarch/i686-pc-linux-gnu'
            #    ),
            #'--libdir={}'.format(
            #    '/multihost/x86_64-pc-linux-gnu/lib'
            #    ),
            ]

        for i in [
                'CC=',
                'CXX=',
                'GCC=',
                '--host=',
                '--build=',
                '--prefix=',
                '--libdir='
                ]:
            for j in range(len(ret) - 1, -1, -1):
                if ret[j].startswith(i):
                    del ret[j]
        ret += [
            '--prefix={}'.format(
                '/multihost/x86_64-pc-linux-gnu'
                ),
            '--host=x86_64-pc-linux-gnu',
            '--build=x86_64-pc-linux-gnu',
            #'CFLAGS=-O2 -fno-builtin-memcpy'
            ]

        if self.get_arch_from_pkgi().startswith('i686'):
            ret += [
                '--libdir={}'.format(
                    '/multihost/x86_64-pc-linux-gnu/lib'
                ),
                ]

        return ret

    def builder_action_configure(self, called_as, log):

        if self.get_host_from_pkgi().startswith('x86_64'):
            self._reconfigure_arch()
            self.override_get_arch_from_pkgi = 'i686-pc-linux-gnu'

        os.makedirs(
            wayround_org.utils.path.join(
                self.get_src_dir(),
                'wine32'
                ),
            exist_ok=True
            )
        ret = super().builder_action_configure(called_as, log)
        return ret
