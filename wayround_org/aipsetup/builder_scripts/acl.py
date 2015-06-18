
import logging
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        return {'subset': 'acl'}

    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('patch', self.builder_action_patch),
            ('autogen', self.builder_action_autogen),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute),
            ('fix_symlinks', self.builder_action_fix_symlinks),
            ('fix_la_file', self.builder_action_fix_la_file)
            ])

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install', 'install-dev', 'install-lib',
                'DESTDIR=' + dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_fix_symlinks(self, called_as, log):
        subset = self.custom_data['subset']

        ret = 0

        try:
            for i in ['lib' + subset + '.a', 'lib' + subset + '.la']:
                ffn = os.path.join(self.dst_dir, 'usr', 'lib', i)

                if os.path.exists(ffn):
                    os.unlink(ffn)

                os.symlink(os.path.join('..', 'libexec', i), ffn)

            for i in ['lib' + subset + '.so']:
                ffn = os.path.join(self.dst_dir, 'usr', 'libexec', i)

                if os.path.exists(ffn):
                    os.unlink(ffn)

                os.symlink(os.path.join('..', 'lib', i), ffn)
        except:
            logging.exception('error')
            ret = 1
        return ret

    def builder_action_fix_la_file(self, called_as, log):
        subset = self.custom_data['subset']

        ret = 0

        la_file_name = os.path.join(
            self.dst_dir, 'usr', 'lib', 'lib' + subset + '.la'
            )

        #print("la_file_name == {}".format(la_file_name))

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
