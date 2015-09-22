
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
        #self.source_configure_reldir = '..'

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
        ret += ['--enable-win64']
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
                #ret['wow64'] = True
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

   # def get_arch_from_pkgi(self):
   #     return 'i686-pc-linux-gnu'

   # def get_multilib_variants_from_pkgi(self):
     #   return ['m32']

    def calculate_pkgconfig_search_paths(self, prefix=None):
        ret = super().calculate_pkgconfig_search_paths(
            prefix='/multihost/x86_64-pc-linux-gnu/multiarch/i686-pc-linux-gnu'
            )
        return ret

    def calculate_C_INCLUDE_PATH(self, prefix=None):
        ret = super().calculate_pkgconfig_search_paths(
            prefix='/multihost/x86_64-pc-linux-gnu/multiarch/i686-pc-linux-gnu'
            )
        return ret

    def calculate_LD_LIBRARY_PATH(self, prefix=None):
        ret = super().calculate_LD_LIBRARY_PATH(
            prefix='/multihost/x86_64-pc-linux-gnu/multiarch/i686-pc-linux-gnu'
            )
        return ret

    def calculate_LIBRARY_PATH(self, prefix=None):
        ret = super().calculate_LIBRARY_PATH(
            prefix='/multihost/x86_64-pc-linux-gnu/multiarch/i686-pc-linux-gnu'
            )
        return ret

    def calculate_PATH(self, prefix=None):
        ret = super().calculate_PATH(
            prefix='/multihost/x86_64-pc-linux-gnu/multiarch/i686-pc-linux-gnu'
            )
        return ret

    def calculate_PATH_dict(self, prefix=None):
        ret = super().calculate_PATH_dict(
            prefix='/multihost/x86_64-pc-linux-gnu/multiarch/i686-pc-linux-gnu'
            )
        return ret

    '''
    def builder_action_configure_define_PATH_list(self):
        ret = super().builder_action_configure_define_PATH_list()

        if self.custom_data['Builder_wow64'] is not None:
            ret += [
                # TODO: no hardcode!
                wayround_org.utils.path.join('/multiarch/x86_64-pc-linux-gnu/bin'),
                wayround_org.utils.path.join('/multiarch/x86_64-pc-linux-gnu/sbin')
                ]

        return ret
    '''

    def builder_action_configure_define_environment(self, called_as, log):
        ret = super().builder_action_configure_define_environment(
            called_as,
            log)

        for i in []:
            if i in ret:
                del ret[i]

        return ret

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
            '--libdir={}'.format(
                '/multihost/x86_64-pc-linux-gnu/lib'
                ),
            ]

        return ret

    def builder_action_configure(self, called_as, log):
        os.makedirs(
            wayround_org.utils.path.join(
                self.get_src_dir(),
                'wine32'
                ),
            exist_ok=True
            )
        ret = super().builder_action_configure(called_as, log)
        return ret

    '''
    def builder_action_build_define_args(self, called_as, log):
        ret = ['depend', 'all']
        ret += super().builder_action_build_define_args(called_as, log)
        return ret
    '''

    def builder_action_build_define_environment(self, called_as, log):
        ret = super().builder_action_build_define_environment(called_as, log)
        for i in ['GCC', 'CC', 'CXX']:
            if i in ret:
                del ret[i]
        return ret

    '''
    def builder_action_build_define_environment(self, called_as, log):
        ret = super().builder_action_build_define_environment(called_as, log)
        #ret['CC'] = 'x86_64-pc-linux-gnu-gcc'
        #ret['GCC'] = 'x86_64-pc-linux-gnu-gcc'
        #ret['CXX'] = 'x86_64-pc-linux-gnu-g++'
        return ret
    '''
