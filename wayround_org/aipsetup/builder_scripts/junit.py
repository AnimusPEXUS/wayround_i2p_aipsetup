

import os.path
import subprocess


import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['configure'])
        del(ret['autogen'])
        return ret

    def define_custom_data(self):

        src_junit_dir = wayround_org.utils.path.join(
            self.src_dir,
            'junit{}'.format(
                self.package_info['pkg_nameinfo']['groups']['version']
                )
            )

        dst_classpath_dir = wayround_org.utils.path.join(
            self.dst_dir,
            'multiarch',
            self.host,
            'lib',
            'java',
            'classpath'
            )

        ret = {
            'src_junit_dir': src_junit_dir,
            'dst_classpath_dir': dst_classpath_dir
            }

        return ret

    def builder_action_build(self, called_as, log):
        p = subprocess.Popen(
            [
                'ant',
                '-Dversion={}'.format(
                    self.package_info['pkg_nameinfo']['groups']['version']
                    ),
                'dist'
                ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):
        os.makedirs(dst_classpath_dir, exist_ok=True)

        shutil.copy(
            wayround_org.utils.path.join(
                src_junit_dir, 'junit-{}.jar'.format(
                    pkg_info['pkg_nameinfo']['groups']['version']
                    )
                ),
            dst_classpath_dir
            )
        return 0
