
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.source_configure_reldir = 'build_unix'
        return None

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        return ret

    def builder_action_configure_define_relative_call(self, called_as, log):
        return True

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            #'--enable-dbm',
            #'--enable-ndbm',
            '--enable-sql',
            '--enable-compat185',
            '--enable-static',
            '--enable-shared',
            '--enable-cxx',
            '--enable-tcl',
            '--with-tcl={}'.format(
                os.path.join(self.host_multiarch_dir, 'lib')
                ),
            ]

    def builder_action_configure_define_script_name(self, called_as, log):
        return os.path.join('..', 'dist', 'configure')

    def builder_action_distribute(self, called_as, log):

        doc_dir = os.path.join(
            self.dst_host_multiarch_dir,
            'share',
            'doc',
            'db')

        os.makedirs(
            doc_dir,
            mode=0o755,
            exist_ok=True
            )

        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'DESTDIR={}'.format(self.dst_dir),
                'docdir={}'.format(
                    os.path.join(
                        self.host_multiarch_dir, 'share', 'doc', 'db'
                        )
                    )
                # it's not a mistake docdir
                # must be eq to /usr/share/doc/db
                # with leading slash
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )

        return ret
