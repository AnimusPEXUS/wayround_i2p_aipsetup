
import re

import wayround_org.utils.path

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.forced_target = False

        self.apply_host_spec_compilers_options = True

        self.source_configure_reldir = 'js/src'

        ret = {}
        # ret['MOZILLA_VERSION']=
        # ret['MOZILLA_UAVERSION']=

        if self.get_package_info()['pkg_info']['name'] == 'mozjs17':
            ret['LIBRARY_NAME'] = 'mozjs-17'

        if self.get_package_info()['pkg_info']['name'] == 'mozjs24':
            ret['LIBRARY_NAME'] = 'mozjs-24'

        if self.get_package_info()['pkg_info']['name'] in [
                'mozjs17',
                'mozjs24'
                ]:
            ret['MOZ_ARCH'] = self.get_arch_from_pkgi()

        return ret

    def _additional_opts(self, libname=False, arch=False):
        ret = []

        if libname:
            if 'LIBRARY_NAME' in self.custom_data:
                ret.append(
                    'LIBRARY_NAME={}'.format(self.custom_data['LIBRARY_NAME'])
                    )

        if arch:
            if 'MOZ_ARCH' in self.custom_data:
                ret.append(self.custom_data['MOZ_ARCH'])

        return ret

    def builder_action_patch(self, called_as, log):
        ret = 0

        milestone_file_path = wayround_org.utils.path.join(
            self.get_src_dir(),
            'js',
            'src',
            'config',
            'milestone.txt'
            )

        with open(milestone_file_path) as f:
            milestone_file_text_lines = f.read().split('\n')

        milestone = None
        for i in milestone_file_text_lines:
            if len(i) != 0 and i[0].isdigit():
                milestone = i
                break

        if not isinstance(milestone, str):
            log.error("can't determine milestone")
            ret = 10

        if ret == 0:

            ver = milestone
            uaver = '.'.join(
                [re.match(r'(\d+)', i).group(1) for i in milestone.split('.')]
                )
            versym = re.match(
                r'^.*\d+(?P<sym>(\w+\d*)?)$', 
                milestone
                ).group('sym')
            ver_major = int(milestone.split('.')[0])

            config_file_path = wayround_org.utils.path.join(
                self.get_src_dir(),
                'js',
                'src',
                'configure'
                )

            with open(config_file_path) as f:
                config_file_text_lines = f.read().split('\n')

            for i in range(len(config_file_text_lines)):
                if config_file_text_lines[i].startswith('MOZILLA_VERSION='):
                    config_file_text_lines[i] = 'MOZILLA_VERSION={}'.format(
                        ver
                        )

                if config_file_text_lines[i].startswith('MOZILLA_UAVERSION='):
                    config_file_text_lines[i] = 'MOZILLA_UAVERSION={}'.format(
                        uaver
                        )

                if config_file_text_lines[i].startswith('MOZILLA_SYMBOLVERSION='):
                    config_file_text_lines[i] = \
                        'MOZILLA_SYMBOLVERSION={}{}'.format(
                            ver_major,
                            versym
                            )



            with open(config_file_path, 'w') as f:
                f.write('\n'.join(config_file_text_lines))

        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        for i in range(len(ret) - 1, -1, -1):
            for j in [
                    'CC=',
                    'CXX=',
                    'GCC=',
                    #'--host=',
                    #'--build=',
                    #'--target=',
                    #'--includedir='
                    ]:
                if ret[i].startswith(j):
                    del ret[i]
                    break

        # ret += self._additional_opts(arch=True)

        return ret

    def builder_action_build_define_args(self, called_as, log):
        ret = super().builder_action_build_define_args(called_as, log)
        ret += self.all_automatic_flags_as_list()

        # ret += self._additional_opts(libname=True)

        return ret

    def builder_action_distribute_define_args(self, called_as, log):
        ret = super().builder_action_distribute_define_args(called_as, log)
        ret += []  # self.all_automatic_flags_as_list()

        # ret += self._additional_opts(libname=True)

        return ret
