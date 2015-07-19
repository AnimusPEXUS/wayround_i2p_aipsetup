
import os.path
import subprocess
import collections

import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        src_ant_dir = wayround_org.utils.path.join(
            self.src_dir,
            'apache-ant-{}'.format(
                self.package_info['pkg_nameinfo']['groups']['version']
                )
            )

        dst_ant_dir = wayround_org.utils.path.join(
            self.dst_host_multiarch_dir, 'lib', 'java', 'apache-ant'
            )

        etc_dir = os.path.join(self.dst_dir, 'etc', 'profile.d', 'SET')

        apacheant009 = os.path.join(etc_dir, '009.apache-ant.{}.sh'.format(self.host_strong))

        return {
            'src_ant_dir': src_ant_dir,
            'dst_ant_dir': dst_ant_dir,
            'etc_dir': etc_dir,
            'apacheant009': apacheant009
            }

    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])

    def builder_action_build(self, called_as, log):
        p = subprocess.Popen(
            [
                'bootstrap/bin/ant',
                #'dist'
                ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):
        os.makedirs(
            self.custom_data['dst_ant_dir'],
            exist_ok=True
            )

        wayround_org.utils.file.copytree(
            self.custom_data['src_ant_dir'],
            self.custom_data['dst_ant_dir'],
            overwrite_files=True,
            clear_before_copy=True,
            dst_must_be_empty=True
            )
    
        # NOTE: disabled because I fink it's not needed
        if False:

            os.makedirs(
                self.custom_data['etc_dir'], 
                exist_ok=True
                )

            fi = open(
                self.custom_data['apacheant009'], 
                'w'
                )
            
            # TODO: may be all such PATH creators better to move away from
            #       builder scripts, so creators don't be deleted with package
            #       removes
            fi.write(
                """\
    #!/bin/bash
    export ANT_HOME='/usr/lib/java/apache-ant'
    export PATH="$PATH:$ANT_HOME/bin"
    """
                )

            fi.close()

        return 0
