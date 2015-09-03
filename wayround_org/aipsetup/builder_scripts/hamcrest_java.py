
import subprocess
import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        dst_classpath_dir = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(),
            'opt',
            'java',
            'classpath'
            )
        
        src_build_dir = wayround_org.utils.path.join(
            self.get_src_dir(),
            'build'
            )
            
        ret = {
            'dst_classpath_dir': dst_classpath_dir,
            'src_build_dir':src_build_dir
            }

        return ret

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        del(ret['configure'])

        ret['build'] = self.builder_action_build
        ret['distribute'] = self.builder_action_distribute

        return ret

    def builder_action_build(self, called_as, log):
        p = subprocess.Popen(
            [
                'ant',
                '-Dversion={}'.format(
                    self.get_package_info()['pkg_nameinfo']['groups']['version']
                    )
                ],
            cwd=self.get_src_dir(),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):

        os.makedirs(self.custom_data['dst_classpath_dir'], exist_ok=True)
        shutil.copy(
            wayround_org.utils.path.join(
                self.custom_data['src_build_dir'], 
                'hamcrest-all-{}.jar'.format(
                    self.get_package_info()['pkg_nameinfo']['groups']['version']
                    )
                ),
            self.custom_data['dst_classpath_dir']
            )
        return 0
