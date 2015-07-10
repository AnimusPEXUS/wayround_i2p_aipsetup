

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        p = subprocess.Popen(
            ['uname', '-r'],
            stdout=subprocess.PIPE
            )
        text = p.communicate()
        p.wait()

        kern_rel = str(text[0].splitlines()[0], encoding='utf-8')

        logging.info("`uname -r' returned: {}".format(kern_rel))

        kdir = os.path.join(
            dst_dir,
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
        makefile_name = os.path.join(self.src_dir, 'Makefile')

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
            logging.exception("Error. See exception message")
            ret = 10
        return ret

    def builder_action_after_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'all',
                'install',
                'PWD=' + self.src_dir,
                'KERNELRELEASE=' + self.custom_data['kern_rel'],
                'DESTDIR=' + self.dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_after_distribute(self, called_as, log):

        kdir = self.custom_data['kdir']

        try:
            files = os.listdir(kdir)

            for i in files:
                fname = os.path.join(kdir, i)
                if os.path.isfile(fname):
                    os.unlink(fname)

        except:
            logging.exception("Error. See exception message")
            ret = 11

        return ret
