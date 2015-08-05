
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        return {'subset': 'acl'}

    def define_actions(self):
        ret = super().define_actions()
        del ret['configure']
        ret['fix_symlinks'] = self.builder_action_fix_symlinks
        ret['fix_la_file'] = self.builder_action_fix_la_file
        return ret

    def builder_action_distribute(self, called_as, log):

        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install', 'install-dev', 'install-lib',
                'DESTDIR={}'.format(self.dst_dir)
                ],
            environment=self.builder_action_make_define_environment(
                called_as,
                log
                ),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_fix_symlinks(self, called_as, log):
        subset = self.custom_data['subset']

        ret = 0

        try:
            for i in ['lib{}.a'.format(subset), 'lib{}.la'.format(subset)]:
                ffn = os.path.join(self.dst_host_multiarch_dir, 'lib', i)

                if os.path.exists(ffn):
                    os.unlink(ffn)

                os.symlink(os.path.join('..', 'libexec', i), ffn)

            for i in ['lib{}.so'.format(subset)]:
                ffn = os.path.join(self.dst_host_multiarch_dir, 'libexec', i)

                if os.path.exists(ffn):
                    os.unlink(ffn)

                os.symlink(os.path.join('..', 'lib', i), ffn)
        except:
            log.exception('error')
            ret = 1
        return ret

    def builder_action_fix_la_file(self, called_as, log):
        subset = self.custom_data['subset']

        ret = 0

        la_file_name = os.path.join(
            self.dst_host_multiarch_dir,
            'lib',
            'lib{}.la'.format(subset)
            )

        # print("la_file_name == {}".format(la_file_name))

        la_file = open(la_file_name)
        lines = la_file.read().splitlines()
        la_file.close()

        for i in range(len(lines)):
            while self.dst_dir in lines[i]:
                lines[i] = lines[i].replace(self.dst_dir, '')

        la_file = open(la_file_name, 'w')
        la_file.write('\n'.join(lines))
        la_file.close()
        return ret
