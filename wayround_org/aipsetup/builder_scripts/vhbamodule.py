

import os.path
import logging
import subprocess

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        self.apply_host_spec_linking_interpreter_option = False
        self.apply_host_spec_linking_lib_dir_options = False
        self.apply_host_spec_compilers_options = True

        p = subprocess.Popen(
            ['uname', '-r'],
            stdout=subprocess.PIPE
            )
        text = p.communicate()
        p.wait()

        kern_rel = str(text[0].splitlines()[0], encoding='utf-8')

        logging.info("`uname -r' returned: {}".format(kern_rel))

        kdir = wayround_org.utils.path.join(
            self.get_dst_dir(),
            'lib',
            'modules',
            kern_rel
            )

        ret = {
            'kdir': kdir,
            'kern_rel': kern_rel
            }
        return ret

    def define_actions(self):
        ret = super().define_actions()
        del ret['autogen']
        del ret['configure']
        del ret['build']
        ret['after_distribute'] = self.builder_action_after_distribute
        return ret

    def builder_action_patch(self, called_as, log):
        makefile_name = wayround_org.utils.path.join(
            self.get_src_dir(),
            'Makefile'
            )

        ret = 0

        try:
            with open(makefile_name, 'r') as makefile:
                lines = makefile.readlines()

            for each in range(len(lines)):
                if lines[each] == '\t$(MAKE) -C $(KDIR) M=$(PWD) $@\n':
                    lines[each] = \
                        '\t$(MAKE) -C $(KDIR) M=$(PWD) INSTALL_MOD_PATH=$(DESTDIR) $@\n'

            with open(makefile_name, 'w') as makefile:
                makefile.writelines(lines)

        except:
            log.exception("Error. See exception message")
            ret = 10
        return ret

    def builder_action_after_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=[],
            arguments=[
                'all',
                'install',
                'PWD={}'.format(self.get_src_dir()),
                'KERNELRELEASE={}'.format(self.custom_data['kern_rel']),
                'DESTDIR={}'.format(self.get_dst_dir()),
                ] + self.all_automatic_flags_as_list(),
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_after_distribute(self, called_as, log):

        ret = 0

        kdir = self.custom_data['kdir']

        try:
            files = os.listdir(kdir)

            for i in files:
                fname = wayround_org.utils.path.join(kdir, i)
                if os.path.isfile(fname):
                    os.unlink(fname)

        except:
            log.exception("Error. See exception message")
            ret = 11

        return ret
