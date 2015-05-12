
import logging
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std

class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure(self, log):

        ret = autotools.configure_high(
            self.buildingsite,
            log=log,
            options=[
                '--enable-audio',
                '--enable-video',
                '--enable-events',
                '--enable-libc',
                '--enable-loads',
                '--enable-file',
                '--enable-alsa',
                '--prefix=' + self.package_info['constitution']['paths']['usr'],
                '--mandir=' + self.package_info['constitution']['paths']['man'],
                '--sysconfdir=' +
                    self.package_info['constitution']['paths']['config'],
                '--localstatedir=' +
                    self.package_info['constitution']['paths']['var'],
                '--enable-shared',
                ] + wayround_org.aipsetup.build.calc_conf_hbt_options(self),
            arguments=[],
            environment={},
            environment_mode='copy',
            source_configure_reldir=self.source_configure_reldir,
            use_separate_buildding_dir=self.separate_build_dir,
            script_name='configure',
            run_script_not_bash=False,
            relative_call=False
            )
        return ret

