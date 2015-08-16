
import os.path
import fnmatch
import shutil
import subprocess

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.utils.path


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        return ret

    def define_custom_data(self):

        makefile_suffix = None

        if fnmatch.fnmatch(self.host, 'i?86-pc-linux-gnu'):
            makefile_suffix = 'linux_any_cpu'
        elif self.host == 'x86_64-pc-linux-gnu':
            makefile_suffix = 'linux_any_cpu'
        else:
            raise Exception("Can't configure")

        dl = wayround_org.aipsetup.build.find_dl(self.host_multiarch_dir)

        CXX = '{}-g++'.format(self.host_strong)
        CC = '{}-gcc'.format(self.host_strong)
        # LOCAL_FLAGS = self.calculate_default_linker_program_gcc_parameter()

        ret = {
            'CXX': CXX,
            'CC': CC,
            #'LOCAL_FLAGS': LOCAL_FLAGS,
            'PREFIX': self.host_multiarch_dir,
            'makefile_suffix': makefile_suffix
            }

        return ret

    def builder_action_configure(self, called_as, log):
        shutil.copy(
            wayround_org.utils.path.join(
                self.src_dir,
                'makefile.{}'.format(
                    self.custom_data['makefile_suffix']
                    )
                ),
            wayround_org.utils.path.join(self.src_dir, 'makefile.machine')
            )
        return 0

    def builder_action_build(self, called_as, log):
        p = subprocess.Popen(
            [
                'make',
                'all3',
                #'7za', '7z',
                'CC={}'.format(self.custom_data['CC']),
                'CXX={}'.format(self.custom_data['CXX']),
                # 'LOCAL_FLAGS={}'.format(self.custom_data['LOCAL_FLAGS']),
                'DEST_HOME={}'.format(self.custom_data['PREFIX']),
                'DEST_DIR={}'.format(self.dst_dir)
                ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):
        p = subprocess.Popen(
            [
                'make',
                'install',
                'CC={}'.format(self.custom_data['CC']),
                'CXX={}'.format(self.custom_data['CXX']),
                #'LOCAL_FLAGS={}'.format(self.custom_data['LOCAL_FLAGS']),
                'DEST_HOME={}'.format(self.custom_data['PREFIX']),
                'DEST_DIR={}'.format(self.dst_dir)
                ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret
