

import os.path
import copy
import subprocess

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std

# TODO: reworkings required

class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        self.apply_host_spec_linking_interpreter_option = False
        self.apply_host_spec_linking_lib_dir_options = False
        self.apply_host_spec_compilers_options = True

        return

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        del(ret['configure'])
        return ret

    def builder_action_configure(self, called_as, log):
        patches = os.listdir(self.get_patches_dir())
        patches.sort()

        if len(patches) == 0:
            logging.error("Patches not supplied")
            ret = 3
        else:

            for i in patches:
                p = subprocess.Popen(
                    ['patch',
                     '-i',
                     wayround_org.utils.path.join(
                         patch_dir,
                         i
                         )
                     ],
                    cwd=self.get_src_dir(),
                    stdout=log.stdout,
                    stderr=log.stderr
                    )
                p.wait()
        return ret

    def builder_action_build(self, called_as, log):
        p = subprocess.Popen(
            ['make',
             'linux'
             ],
            cwd=self.get_src_dir(),
            env=copy.deepcopy(os.environ).update(
                self.all_automatic_flags_as_dict()
                ),
            stdout=log.stdout,
            stderr=log.stderr
            )
        if p.wait() != 0:
            ret = 2
        return ret

    def builder_action_distrinute(self, called_as, log):
        # make dirs

        for i in [
                'usr/lib',
                'usr/bin',
                'usr/share/man',
                'usr/include',
                ]:
            pp = wayround_org.utils.path.join(self.get_dst_dir(), i)
            if not os.path.isdir(pp):
                os.makedirs(pp)

        # shared

        shared_dir = wayround_org.utils.path.join(self.get_src_dir(), 'shared')

        shared = os.listdir(shared_dir)

        for i in shared:
            if i.startswith('libwrap'):
                p = subprocess.Popen(
                    [
                        'cp',
                        wayround_org.utils.path.join(shared_dir, i),
                        wayround_org.utils.path.join(
                            self.get_dst_dir(),
                            'usr/lib'
                        )
                    ]
                )
                if p.wait() != 0:
                    ret = 5

        # *.a

        for i in os.listdir(self.get_src_dir()):
            if i.endswith('.a'):
                p = subprocess.Popen(
                    [
                        'cp',
                        wayround_org.utils.path.join(self.get_src_dir(), i),
                        wayround_org.utils.path.join(
                            self.get_dst_dir(),
                            'usr/lib'
                        )
                    ]
                )
                if p.wait() != 0:
                    ret = 8

        # *.h

        for i in os.listdir(self.get_src_dir()):
            if i.endswith('.h'):
                p = subprocess.Popen(
                    [
                        'cp',
                        wayround_org.utils.path.join(self.get_src_dir(), i),
                        wayround_org.utils.path.join(
                            self.get_dst_dir(),
                            'usr/include'
                        )
                    ]
                )
                if p.wait() != 0:
                    ret = 8

        # executables

        for i in ['safe_finger', 'tcpd', 'tcpdchk', 'tcpdmatch', 'try-from']:
            p = subprocess.Popen(
                ['cp',
                 wayround_org.utils.path.join(self.get_src_dir(), i),
                 wayround_org.utils.path.join(self.get_dst_dir(), 'usr/bin')
                 ]
            )
            if p.wait() != 0:
                ret = 6

        # man pages

        for i in range(10):
            dd = wayround_org.utils.path.join(
                self.get_dst_dir(),
                'usr',
                'share',
                'man',
                'man{}'.format(i))
            if not os.path.isdir(dd):
                os.makedirs(dd)

            b = glob.glob(self.get_src_dir() + '/*.{}'.format(i))

            for j in b:
                p = subprocess.Popen(
                    ['cp',
                     wayround_org.utils.path.join(j),
                     wayround_org.utils.path.join(dd, os.path.basename(j))
                     ]
                )
                if p.wait() != 0:
                    ret = 7
        return ret
