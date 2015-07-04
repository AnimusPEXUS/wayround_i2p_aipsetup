
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

        dl = wayround_org.aipsetup.build.find_dl(
            os.path.join(
                '/',
                'multiarch',
                self.host
                )
            )

        CXX = '{}-g++'.format(self.host)
        CC = '{}-gcc'.format(self.host)
        LOCAL_FLAGS = '-Wl,--dynamic-linker=' + dl

        ret = {
            'CXX': CXX,
            'CC': CC,
            'LOCAL_FLAGS': LOCAL_FLAGS,
            'PREFIX': wayround_org.utils.path.join(
                '/multiarch', self.host
                ),
            'makefile_suffix': makefile_suffix
            }

        return ret

    def builder_action_configure(self, called_as, log):
        shutil.copy(
            os.path.join(
                self.src_dir,
                'makefile.{}'.format(
                    self.custom_data['makefile_suffix']
                    )
                ),
            os.path.join(self.src_dir, 'makefile.machine')
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
                'LOCAL_FLAGS={}'.format(self.custom_data['LOCAL_FLAGS']),
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
                'LOCAL_FLAGS={}'.format(self.custom_data['LOCAL_FLAGS']),
                'DEST_HOME={}'.format(self.custom_data['PREFIX']),
                'DEST_DIR={}'.format(self.dst_dir)
                ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()        
        return ret


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
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

        src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(buildingsite)

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                wayround_org.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'configure' in actions and ret == 0:
            shutil.copy(
                os.path.join(src_dir, 'makefile.linux_any_cpu'),
                os.path.join(src_dir, 'makefile.machine')
                )

        if 'build' in actions and ret == 0:
            p = subprocess.Popen(
                ['make', 'all3'],
                cwd=src_dir,
                )
            ret = p.wait()

        if 'distribute' in actions and ret == 0:

            fn = os.path.join(src_dir, 'install.sh')

            f = open(fn)
            lines = f.read().splitlines()
            f.close()

            for i in range(len(lines)):

                if lines[i] == 'DEST_HOME=/usr/local':
                    lines[i] = 'DEST_HOME=/usr'

                if lines[i] == 'DEST_DIR=':
                    lines[i] = 'DEST_DIR={}'.format(dst_dir)

            f = open(fn, 'w')
            f.write('\n'.join(lines))
            f.close()

            p = subprocess.Popen(
                ['make',
                 'install',
                 'DEST_HOME=/usr',
                 'DEST_DIR={}'.format(dst_dir)
                 ],
                cwd=src_dir
                )
            ret = p.wait()

    return ret
