
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

        self.separate_build_dir = wayround_org.utils.path.join(self.get_src_dir(), 'wine64')
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
        os.makedirs(wayround_org.utils.path.join(self.get_src_dir(), 'wine64'), exist_ok=True)
        ret = super().builder_action_configure(called_as, log)
        return ret

    # def builder_action_configure_define_environment


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        self.separate_build_dir = wayround_org.utils.path.join(self.get_src_dir(), 'wine32')

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
                ('distribute_wow64', b64_actions['distribute']),
                ]

        ret_l += [
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ]

        if self.custom_data['Builder_wow64'] is not None:

            ret_l += [
                # ('distribute_wow64', b64_actions['distribute'])
                ]

        ret = collections.OrderedDict(ret_l)
        return ret

    def builder_action_configure_define_environment(self, called_as, log):
        ret = super().builder_action_configure_define_environment(
            called_as,
            log)
        del ret['PATH']
        return ret

    def calculate_pkgconfig_search_paths(self):

        ret = []

        for i in [
                wayround_org.utils.path.join(
                    '/multiarch/i686-pc-linux-gnu',
                    'share',
                    'pkgconfig'),
                wayround_org.utils.path.join(
                    '/multiarch/i686-pc-linux-gnu',
                    'lib',
                    'pkgconfig'),
                wayround_org.utils.path.join(
                    '/multiarch/i686-pc-linux-gnu',
                    'lib32',
                    'pkgconfig'),
                wayround_org.utils.path.join(
                    '/multiarch/i686-pc-linux-gnu',
                    'libx32',
                    'pkgconfig'),
                wayround_org.utils.path.join(
                    '/multiarch/i686-pc-linux-gnu',
                    'lib64',
                    'pkgconfig'),
                ]:

            if os.path.isdir(i):
                ret.append(i)

        ret += super().calculate_pkgconfig_search_paths()

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

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        if self.custom_data['Builder_wow64'] is not None:

            ret += [
                '--with-wine64={}'.format(
                    wayround_org.utils.path.join(self.get_src_dir(), 'wine64')
                    )
                ]

            for i in range(len(ret) - 1, -1, -1):
                for j in [
                        #'--build=',
                        #'--host=',
                        #'--target=',
                        ]:
                    if ret[i].startswith(j):
                        del ret[i]
                        break

            for i in range(len(ret) - 1, -1, -1):
                for j in [
                        #'CC=',
                        #'GCC=',
                        #'CXX=',
                        ]:
                    if ret[i].startswith(j):
                        del ret[i]
                        break

            ret += [
                #'LD={}'.format(
                #    wayround_org.utils.file.which(
                #        'ld',
                #        '/multiarch/x86_64-pc-linux-gnu'
                #        )
                #    )
                ]

            ret += [
                #'CC=x86_64-pc-linux-gnu-gcc',
                #'GCC=x86_64-pc-linux-gnu-gcc',
                #'CXX=x86_64-pc-linux-gnu-g++',
                ]

            # TODO: hardcode is bad
            ret += [
                #'--host=i686-pc-linux-gnu',
                #'--build=i686-pc-linux-gnu'
                ]

            ret += [
                #'LDFLAGS='+
                #' -L{}'.format('/multiarch/i686-pc-linux-gnu/lib') +
                #' -L{}'.format('/multiarch/x86_64-pc-linux-gnu/lib') +
                #' -L{}'.format('/multiarch/x86_64-pc-linux-gnu/lib64') +
                #' -L{}'.format('/multiarch/i686-pc-linux-gnu/lib/gcc/i686-pc-linux-gnu/5.2.0/')
                #' --sysroot=/ ' +
                #' -Wl,--sysroot=/ '
                #,
                #'CFLAGS=--sysroot=/'
                ]

        return ret

    def builder_action_configure(self, called_as, log):
        os.makedirs(wayround_org.utils.path.join(self.get_src_dir(), 'wine32'), exist_ok=True)
        ret = super().builder_action_configure(called_as, log)
        return ret

    '''
    def builder_action_build_define_args(self, called_as, log):
        ret = ['depend', 'all']
        ret += super().builder_action_build_define_args(called_as, log)
        return ret
    '''

    def builder_action_build_define_environment(self, called_as, log):
        return {}

    '''
    def builder_action_build_define_environment(self, called_as, log):
        ret = super().builder_action_build_define_environment(called_as, log)
        #ret['CC'] = 'x86_64-pc-linux-gnu-gcc'
        #ret['GCC'] = 'x86_64-pc-linux-gnu-gcc'
        #ret['CXX'] = 'x86_64-pc-linux-gnu-g++'
        return ret
    '''
